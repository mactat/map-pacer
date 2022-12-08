import yaml
import argparse


parser = argparse.ArgumentParser(description='Change resources')
parser.add_argument('--config', type=str, default='docker-swarm.yml', help='config file')
parser.add_argument('--limit-memory', type=int, default=512, help='memory')
parser.add_argument('--limit-cpu', type=float, default=0.5, help='cpu')
parser.add_argument('--reservation-memory', type=int, default=128, help='memory')
parser.add_argument('--reservation-cpu', type=float, default=0.25, help='cpu')
args = parser.parse_args()

# open for read and write
with open(args.config, 'r+') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    # replace values
    config['services']['agent']['deploy']['resources']['limits']['memory'] = f"{args.limit_memory}M"
    config['services']['agent']['deploy']['resources']['limits']['cpu'] = args.limit_cpu
    config['services']['agent']['deploy']['resources']['reservations']['memory'] = f"{args.reservation_memory}M"
    config['services']['agent']['deploy']['resources']['reservations']['cpu'] = args.reservation_cpu
    # write back to file
    f.seek(0)
    yaml.dump(config, f, default_flow_style=False)

# Example of execution: 
# python3 change_resources.py --limit-memory 100 --limit-cpu 0.1 --reservation-memory 50 --reservation-cpu 0.05
