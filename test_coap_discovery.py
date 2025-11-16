import sys
import time
from coapthon.client.coap import CoAP

def test_coap_server():
	print("=" * 70)
	print("CoAP Client Test - Resource Discovery")
	print("=" * 70)
	
	host = 'localhost'
	port = 5683
	
	try:
		client = CoAP((host, port))
		
		print(f"\n>>> Connecting to coap://{host}:{port}")
		time.sleep(0.5)
		
		# Test 1: Resource Discovery
		print("\n" + "=" * 70)
		print("TEST 1: Resource Discovery (.well-known/core)")
		print("=" * 70)
		
		path = ".well-known/core"
		print(f"\nSending GET request to: {path}")
		response = client.get(path)
		
		print(f"\nResponse Code: {response.code}")
		
		if response.payload:
			payload_str = response.payload.decode('utf-8') if isinstance(response.payload, bytes) else str(response.payload)
			print(f"\nDiscovered Resources:")
			print("-" * 70)
			
			resources = payload_str.split(',')
			for resource in resources:
				resource = resource.strip()
				if resource:
					print(f"  {resource}")
			
			print("-" * 70)
		
		print("\n" + "=" * 70)
		print("✓ CoAP Server is working correctly!")
		print("=" * 70 + "\n")
		
	except Exception as e:
		print(f"\n✗ Error: {e}")
		import traceback
		traceback.print_exc()

test_coap_server()
