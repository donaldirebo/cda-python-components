from coapthon.client.coap import CoAP
import time

client = CoAP((('localhost', 5683)), starting_mid=1, callback=None)

# Resource discovery
print("\n" + "="*70)
print("CoAP Resource Discovery")
print("="*70 + "\n")

response = client.get(".well-known/core")
print(f"Response Code: {response.code}")

if response.payload:
    payload = response.payload.decode('utf-8') if isinstance(response.payload, bytes) else str(response.payload)
    print(f"\nDiscovered Resources:\n{payload}\n")
    
    resources = payload.split(',')
    print("Parsed Resources:")
    for resource in resources:
        if resource.strip():
            print(f"  {resource.strip()}")

print("\n" + "="*70 + "\n")
