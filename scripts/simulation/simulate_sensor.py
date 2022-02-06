from argparse import ArgumentParser
import csv
from time import sleep
import datetime
from typing import NamedTuple
import requests

class SimulationConfig(NamedTuple):
	file: str
	url: str
	device_id: int
	delay: int
	token: str
	version: str

def simulate(config: SimulationConfig):
	print('================================================================================================')
	print(f'Simulating device ID {config.device_id} using data from {config.file}')
	print(f'Targeting {config.url}/{config.version} with delay {config.delay}')
	print('================================================================================================')

	with open(config.file, mode='r') as csv_file:
		csv_reader = csv.DictReader(csv_file)

		for row in csv_reader:
			payload = {
				**row,
				'timestamp': datetime.datetime.now().isoformat()
			}
			print(f'Sending: {payload}')
			res = requests.post(f'{config.url}/{config.version}/devices/{config.device_id}/data', json=payload)

			if not res.ok:
				print(f'Request failed with code: {res.status_code}')
				print(res.json())

			print(f'Sleeping for {config.delay} seconds')
			sleep(config.delay)

if __name__ == '__main__':
	parser = ArgumentParser(description='Flourish Device Simulation')
	parser.add_argument('-f', '--file', dest='file', type=str, help='CSV file to use', required=True)
	parser.add_argument('-u', '--url', dest='url', type=str, default='http://localhost:5000', help='URL to target')
	parser.add_argument('-v', '--version', dest='version', type=str, default='v1', help='API version to target')
	parser.add_argument('-d', '--delay', dest='delay', type=int, default=5, help='Delay between requests, in seconds')
	parser.add_argument('-i', '--id', dest='device_id', type=int, help='ID of device being simulated', required=True)
	# TODO: make required when auth is in place
	parser.add_argument('-t', '--token', dest='token', type=str, help='Authentication token of device being simulated')

	args = parser.parse_args()

	config = SimulationConfig(file=args.file, url=args.url, device_id=args.device_id, delay=args.delay, token=args.token, version=args.version)
	simulate(config)
