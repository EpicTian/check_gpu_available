from os import popen, system
import sys
from time import sleep
from torch.cuda import device_count

cmd = 'python your_script.py' # Script which you want to execute.



def gpu_info(gpu_index):
    # Explanation of parameters: 
    # 1. gpu_index: The ID of GPU.
    gpu_status = popen('nvidia-smi | grep %').read().split('\n')[gpu_index].split('|')
    power = int(gpu_status[1].split()[-3][:-1])
    memory = int(gpu_status[2].split('/')[0].strip()[:-3])
    total_memory = int(gpu_status[2].split('/')[1].strip()[:-3])
    men_percent = (memory / total_memory) * 100.0
    gpu_utli = float(gpu_status[3].split()[0][:-1])
    return power, memory, total_memory, men_percent, gpu_utli



def gpu_available(gpu_usage_demand:float=50.0, men_usage_demand: float=50.0, 
                men_demand: float=1024.0, interval: int=20, execute: bool=False):
    ## Explanation of parameters: ##
    # 1. gpu_usage_demand: The required percentage (%) of available GPU-Utilization, default 50.00%.
    # 2. men_usage_demand: The required percentage (%) of available GPU memory, default 50.00%.
    #                      This parameter will be ingored if "gpu_usage_demand" is NOT 0.
    # 3. men_demand: The required available GPU memory, default 1024MiB. 
    #                This parameter will be ingored if "gpu_usage_demand" or "men_usage_demand" is NOT 0.
    # 4. interval: Sleep for interval before starting checking, default 20 seconds.
    # 5. execute: If True, execute the script. If False, do NOT execute the script 
    #             and return the available GPU ID. Default False.
    if not 0.0 <= gpu_usage_demand <= 100.0:
        raise ValueError("Invalid gpu_usage_demand value: {:.2f}%.".format(gpu_usage_demand))
    if not 0.0 <= men_usage_demand <= 100.0:
        raise ValueError("Invalid men_usage_demand value: {:.2f}%.".format(men_usage_demand))
    if gpu_usage_demand:
        print('The required percentage of available GPU-Utilization is {:.2f}%.'.format(gpu_usage_demand))
    elif men_usage_demand:
        print('The required percentage of available GPU memory is {:.2f}%.'.format(men_usage_demand))
    else:
        print('The required available GPU memory is {:.0f} MiB.'.format(men_demand))
    
    print('\nSleep for {:.0f} seconds before starting checking GPUs.'.format(interval))
    id = list(range(device_count()))
    max_total_men = 0
    waitting = True
    while waitting:
        sleep(interval)
        for gpu_id in id:
            gpu_power, gpu_memory, toal_memory, men_percent, gpu_utli = gpu_info(gpu_id)
            if toal_memory > max_total_men:
                max_total_men = toal_memory
            
            if gpu_id == id[-1] and max_total_men < men_demand:
               raise Exception("Invalid men_demand value: {} MiB. Max GPU memory is {:.0f} MiB.".format(men_demand,max_total_men))

            for i in range(5):# Check GPU[gpu_id] for 5 seconds.
                available_gpu_utli = 100.0 - gpu_utli
                available_mem_usage = 100.0 - men_percent
                available_men = toal_memory - gpu_memory
                if gpu_usage_demand and gpu_usage_demand <= available_gpu_utli:
                    waitting = False
                    print('\nNow GPU[ID {:.0f}] available GPU-Utilization: {:.2f}%.'.format(gpu_id,available_gpu_utli))
                    break
                elif not gpu_usage_demand and men_usage_demand and men_usage_demand <= available_mem_usage:
                    waitting = False
                    print('\nNow GPU[ID {:.0f}] available memory usage: {:.2f}%.'.format(gpu_id,available_mem_usage))
                    break
                elif not gpu_usage_demand and not men_usage_demand and men_demand <= available_men:
                    waitting = False
                    print('\nNow GPU[ID {:.0f}] available memory: {:.0f} MiB.'.format(gpu_id,available_men))
                    break
                symbol = 'Monitoring: ' + '>' * (i+1) + ' ' * (4 - i) + '|'
                gpu = '[GPU:%d]' % gpu_id
                gpu_utli_str = 'GPU-Utilization {:.2f}% |'.format(gpu_utli)
                gpu_memory_str = 'Memory in use: %dMiB / %dMiB |' % (gpu_memory,toal_memory)
                gpu_memory_per_str = 'Memory Usage: {:.2f}% |'.format(men_percent)
                sys.stdout.write('\r' + gpu + ' '+ gpu_utli_str +' ' + gpu_memory_str + ' ' + gpu_memory_per_str+ ' ' + symbol)
                sys.stdout.flush()
                sleep(1)
            if not waitting:
                break
    if execute:
        system(cmd)
    else:
        return gpu_id



if __name__ == '__main__':
    print(gpu_available(50, 0.0, 0))
