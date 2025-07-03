import numpy as np
import pandas as pd
import torch
import mmh3
import random
import statistics
import math
import os
from scipy.stats import norm,scoreatpercentile
import itertools
import hashlib

def set_params(model, data, learning_rate):
  for name, param in model.named_parameters():
    if param.requires_grad:
        param.data = param.data + (data[name]*learning_rate)


def set_params_fedsketch(model, data):
  for name, param in model.named_parameters():
        param.data = data[name]
        
def get_params(model):
  param_dict = {}
  for name, param in model.named_parameters():
    if param.requires_grad:
        param_dict[name] = param.clone() #copy.deepcopy(param.clone())
  return param_dict

def delta_weights(new_weights,old_weights):

  delta = { k: v - old_weights[k] for k, v in new_weights.items() if k in old_weights }
  return delta

def get_random_hashfunc(_max=1024, seed=None):
    seed = seed or os.urandom(10)
    seed_hash_func = hashlib.md5(seed)
    def hashfunc(n):
        func = seed_hash_func.copy()
        func.update(n.to_bytes(n.bit_length(), 'big'))
        return int.from_bytes(func.digest(), 'big') % _max
    return hashfunc

#@profile
def CountSketchFunction_pytorch(vector,sketch,length,width,index_hash_functions,weight_index=None):
    #vector_index = range(len(vector))
    #length_index = range(length)
    #sign_goal = [(mmh3.hash(str(hash((weight_index,i))),j) % 2) * 2 - 1 for i in vector_index for j in length_index]
    #increment_goal = [mmh3.hash(str(hash((weight_index,i))),j)%width for i in vector_index for j in length_index]
    #colision_number = {}
    for j in range(length):
      for i in range(len(vector)):
          sign_hash = mmh3.hash(str(i),j) % 2
          sign_value = sign_hash * 2 - 1
          #mmh3.hash(str(i),j)%width
          #if not index_hash(i) in colision_number:
          #  colision_number[index_hash(i)] = 0
          #else:
          #  colision_number[index_hash(i)] += 1
          sketch[j,index_hash_functions[j](i)] += sign_value*vector[i]
#
def QuerySketchFunction_pytorch(start_index,end_index,sketch,length,width,index_hash_functions):
    new_weights = []
    for i in range(start_index,end_index):
        m = []
        for j in range(length):
              sign_hash = mmh3.hash(str(i),j) % 2
              sign_value = sign_hash * 2 - 1
              m.append(sign_value*sketch[j][index_hash_functions[j](i)])
        new_weights.append(statistics.median(m))
    return new_weights
#@profile
def add_weigths_to_sketch_pytorch(weights,compression=0.7, length = 7,index_hash_functions = None):
  convert = [torch.flatten(v) for k,v in weights.items()]
  convert = list(itertools.chain.from_iterable(convert))
  convert = [v.item() for v in convert]
  #biggest_number_elements = np.max([value.numel() for key, value in new_weights.items()])
  width = int(len(convert)*compression)
  sketch = np.zeros((length,width))
  CountSketchFunction_pytorch(convert,sketch,length,width,index_hash_functions)
  return sketch

def query_weigths_sketch_pytorch(weights,length,sketch,index_hash_functions):
  convert = [v.numel() for k,v in weights.items()]
  sizes = [v.size() for k,v in weights.items()]
  keys = [k for k,v in weights.items()]
  n_weights = {}
  start_index = 0
  end_index = 0
  for i in range(len(convert)):
    end_index+=convert[i]
    query = QuerySketchFunction_pytorch(start_index,end_index,sketch,length,len(sketch[0]),index_hash_functions)
    query = torch.tensor(query)
    query = query.reshape(sizes[i])
    n_weights[keys[i]] = query
    start_index += convert[i]
  return n_weights

def epsilon_estimation_pytorch(weights,sketch,percentile):
  convert = [torch.flatten(v) for k,v in weights.items()]
  convert = list(itertools.chain.from_iterable(convert))
  convert = [v.item() for v in convert]
  mu, std = norm.fit(convert)
  alpha = np.percentile(np.abs(convert), 90)
  
  n = len(convert)
  t = sketch.shape[0]
  k = sketch.shape[1]
  if alpha == 0:
    alpha = 1
  if (n-k) == 0:
    n = 1
    k = 0.1
  numerator = (alpha**2)*k*(k-1)
  denominator = (std**2)*(n-2)
  multiplyer = 1+np.log(n-k)
  left_side = (numerator/denominator)*multiplyer
  beta = -1/(left_side - 0.5)
  if beta < 0:
    beta = 0.0000000001
  episolon = t*np.log(1+(beta*left_side))
  #numerator = ((std)*(n-2))
  #denominator = (alpha**2)*k*(k-1)*(1+math.log(n-k))
  #beta = (2*numerator)/denominator
#
  #episolon = t*math.log(1+(beta*numerator)/denominator)
  return episolon


def differential_garantee_pytorch(weights,sketch,desired_episilon,percentile):
  episilon = epsilon_estimation_pytorch(weights,sketch,percentile)

  print("Episilion " + str(episilon))
  if episilon > desired_episilon:
    noise = np.random.laplace(0, 1.0/episilon, 1)
    sketch += noise

def compare_and_zero_pytorch(x,y):
  comparison = []
  for i in range(len(x)):
    comparison.append((torch.abs(x[i])-torch.abs(y[i]),i))
  comparison = sorted(
    comparison,
    key=lambda x: x[0]
  )
  new_x = torch.zeros(len(x))
  for i in range(len(comparison)):
    if i <= int(len(comparison)*0.5):
      new_x[comparison[i][1]] = x[comparison[i][1]]
    else:
      new_x[comparison[i][1]] = 0
  return new_x

def compare_and_zero_weight_list(new_weights,old_weights):
  for key, value in new_weights.items():
      shape = value.size()
      if len(shape) > 1 and shape[0] > 1:
            for i in range(len(value)):
              new_weights[key][i] = torch.Tensor(compare_and_zero_pytorch(new_weights[key][i],old_weights[key][i]))
      elif len(shape) > 1 and shape[0] == 1:
        new_weights[key][0] = torch.Tensor(compare_and_zero_pytorch(new_weights[key][0],old_weights[key][0]))
      elif len(shape) == 1:
        new_weights[key] = torch.Tensor(compare_and_zero_pytorch(new_weights[key],old_weights[key]))
      else:
        new_weights[key] = torch.Tensor(new_weights[key])

def compress(new_weights,compression, length, desired_episilon, percentile,index_hash_functions):
  sketch = add_weigths_to_sketch_pytorch(new_weights,compression,length,index_hash_functions)
  return sketch



def decompress(n_weights,sketch, length, min, max,index_hash_functions):
  n_weights = query_weigths_sketch_pytorch(n_weights,length,sketch,index_hash_functions)
  return n_weights

def epsilon_estimation(weights, sketch,percentile):
  convert = [torch.flatten(v) for k,v in weights.items()]
  convert = list(itertools.chain.from_iterable(convert))
  convert = [v.item() for v in convert]
  mu, std = norm.fit(convert)
  alpha = np.percentile(convert, percentile)
  n = len(convert)
  t = sketch.shape[0]
  k = sketch.shape[1]
  if alpha == 0:
    alpha = 1
  if (n-k) == 0:
    n = 1
    k = 0.1
  numerator = (alpha**2)*k*(k-1)
  denominator = (std**2)*(n-2)
  multiplyer = 1+np.log(n-k)
  left_side = (numerator/denominator)*multiplyer
  beta = -1/(left_side - 0.5)
  if beta < 0:
    beta = 0.0000001
  episolon = t*np.log(1+(beta*left_side))
  return episolon

def differential_garantee(weights,sketch,desired_episilon,percentile):
  episilon = epsilon_estimation(weights,sketch,percentile)

  print("Episilion " + str(episilon))
  if episilon > desired_episilon:
    noise = np.random.laplace(0, 1.0/episilon, 1)
    sketch += noise


def CountSketchFunction(vector,sketch,length,width,weight_index=None):
    random.seed(0)
    seed = [random.randint(0,10000) for _ in range(length)]
    sign_seed = [random.randint(0,10000) for _ in range(length)]
    for i in range(len(vector)):
     for j in range(length):
          #sketch[j][hash_family(j+1,i)] =  sketch[j][hash_family(j+1,i)] + sign(hash_family(j+1,i))*vector[i]
          sign_hash = mmh3.hash(str(i),sign_seed[j]) % 2
          sign_value = sign_hash * 2 - 1
          sketch[j][mmh3.hash(str(i),seed[j])%width] =  sketch[j][mmh3.hash(str(i),seed[j])%width] + sign_value*vector[i]
def QuerySketchFunction(weights,length,width,sketch,weight_index=None):
    new_weights = np.zeros(weights.shape)
    random.seed(0)
    seed = [random.randint(0,10000) for _ in range(length)]
    sign_seed = [random.randint(0,10000) for _ in range(length)]
    for i in range(len(weights)):
        m = []
        for j in range(length):
          if weight_index != None:
              sign_hash = mmh3.hash(str(hash((weight_index,i))),sign_seed[j]) % 2
              sign_value = sign_hash * 2 - 1
              m.append(sign_value*sketch[j][mmh3.hash(str(hash((weight_index,i))),seed[j])%width])
          else:
            #m.append(sketch[j][hash_family(j+1,i)])
              sign_hash = mmh3.hash(str(i),sign_seed[j]) % 2
              sign_value = sign_hash * 2 - 1
              m.append(sign_value*sketch[j][mmh3.hash(str(i),seed[j])%width])
        new_weights[i] = statistics.median(m)
    return new_weights 