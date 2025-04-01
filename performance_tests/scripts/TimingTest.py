import requests
import time

BASE_URL = "http://localhost:4567"
SAMPLE_INDEX = 42  # Choose any index you want to compare across batches

def send_batch_requests(batch_size):
    responses = []
    print(f"\nStarting batch of {batch_size} requests...")
    start = time.time()

    for i in range(batch_size):
        payload = {
            "title": f"Batch Test {i}",
            "description": "Performance testing"
        }
        try:
            res = requests.post(f"{BASE_URL}/todos", json=payload)
            responses.append(res.json())
        except Exception as e:
            print(f"Request {i} failed: {e}")
            responses.append(None)

    end = time.time()
    print(f"Completed {batch_size} requests in {end - start:.2f} seconds")
    return responses

def compare_samples(res1, res2, res3):
    print("\nComparing sample responses from each batch:")
    for idx, res in enumerate([res1, res2, res3], start=1):
        print(f"Sample from Batch {idx}: {res}")

    all_same = res1 == res2 == res3
    print("\n✅ Responses are the same!" if all_same else "\n❌ Responses differ!")

def main():
    batch_1000 = send_batch_requests(1000)
    batch_10000 = send_batch_requests(10000)
    batch_100000 = send_batch_requests(100000)

    sample_1000 = batch_1000[SAMPLE_INDEX] if len(batch_1000) > SAMPLE_INDEX else None
    sample_10000 = batch_10000[SAMPLE_INDEX] if len(batch_10000) > SAMPLE_INDEX else None
    sample_100000 = batch_100000[SAMPLE_INDEX] if len(batch_100000) > SAMPLE_INDEX else None

    compare_samples(sample_1000, sample_10000, sample_100000)

if __name__ == "__main__":
    main()
