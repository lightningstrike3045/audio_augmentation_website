import audiomentations
import soundfile as sf
import numpy as np
import os
from inspect import signature
# Map string to function
string_to_function = {
    "time stretch": audiomentations.TimeStretch,
    "pitch shift": audiomentations.PitchShift,
    "air absorption": audiomentations.AirAbsorption,
    "aliasing": audiomentations.Aliasing,
    "band pass filter": audiomentations.BandPassFilter,
    "band stop filter": audiomentations.BandStopFilter,
    "reverse" : audiomentations.Reverse,

}
dtype_to_string = {
    float : "float",
    int : "int",
    str : "string",
    bool : "bool",
}
# TODO : Implement customizable params
def search_for_method(method_name: str):
    if method_name not in string_to_function.keys():
        return None, "No method found"
    foo =  string_to_function[method_name]
    params = signature(foo).parameters
    parameter_list = []
    for k in params.keys():
        p = params[k]
        if p.name == "p":
            break
        dtype = p.annotation
        default = p.default
        parameter_list.append({
            "name":p.name,
            "dtype":dtype_to_string[dtype],
            "default":default
        })
    return foo, parameter_list


    
# Read audio to numpy array
def file_to_samples(audio_file_path):
    data, sample_rate = sf.read(audio_file_path, always_2d=True)
    data = data.T
    print(data.shape)
    return data, sample_rate

# Create an augmentation function based on method list
def build_augmentation(method_list, use_param_list = False,param_list = []):
    methods = []
    for i in range(len(method_list)):
        foo, _ = search_for_method(method_list[i])
        sig = signature(foo)
        if use_param_list:
            methods.append(foo(*param_list[i],p=1))
        else:
            methods.append(foo(p=1))
    augment = audiomentations.Compose(methods)
    return augment




# Combine functions and augment data for one files
def process(audio_file, method_list, param_list = []):
    samples, rate = file_to_samples(audio_file)
    use_param_list = not (param_list == [])
    augment = build_augmentation(method_list, use_param_list,param_list)
    processed = augment(samples, sample_rate=rate)
    name = os.path.basename(audio_file)
    return processed, rate
# Convert entire folders 

def bulk_process(input_folder, method_list, target_folder):
    files = os.listdir(input_folder)
    for f in files:
        samples, rate = process(input_folder + f, method_list)
        sf.write(f"{target_folder}/processed_{f}",samples.T,rate)