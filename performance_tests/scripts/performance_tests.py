import requests
import time
import csv
import psutil
import os
import random

BASE_URL = "http://localhost:4567"
SAMPLE_INDEX = 42
random.seed(42)

def monitor_resources():
    process = psutil.Process(os.getpid())
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = process.memory_info().rss / (1024 * 1024)  # in MB
    return cpu_percent, memory

def send_requests(operation, batch_size):
    times = []
    statuses = []
    print(f"\n➡️ Starting '{operation}' operation with {batch_size} requests...")
    
    for i in range(batch_size):
        payload = {
            "title": f"PerfTest {random.randint(1000, 9999)}",
            "description": "Performance test object"
        }

        start = time.time()

        try:
            if operation == "create":
                response = requests.post(f"{BASE_URL}/todos", json=payload)
            elif operation == "delete":
                response = requests.delete(f"{BASE_URL}/todos/{random.randint(1, 1000)}")
            elif operation == "update":
                response = requests.post(f"{BASE_URL}/todos/{random.randint(1, 1000)}", json={"title": "Updated Title"})
            else:
                raise ValueError("Unknown operation")

            elapsed = time.time() - start
            times.append(elapsed)
            statuses.append(response.status_code)
        except Exception as e:
            print(f"Error during {operation} at index {i}: {e}")
            times.append(None)
            statuses.append("Error")

    avg_time = sum(filter(None, times)) / len([t for t in times if t is not None])
    print(f"Completed {batch_size} '{operation}' requests. Avg Time: {avg_time:.4f}s")
    
    cpu, memory = monitor_resources()
    print(f"🔍 CPU: {cpu}%, Memory: {memory:.2f}MB")

    return times, statuses, cpu, memory


def create_update_delete_sequence(batch_size=100):
    times = []
    status_tracker = []
    print(f"\n Starting batch of {batch_size} create-update-delete sequences...")

    for i in range(batch_size):
        start = time.time()
        try:
            # Create
            payload_create = {"title": f"Perf Project {i}", "description": "Perf test"}
            create_res = requests.post(f"{BASE_URL}/projects", json=payload_create)
            #assert create_res.status_code == 201
            project_id = create_res.json()["id"]

            # Update
            payload_update = {"title": f"Updated Title {i}"}
            update_res = requests.post(f"{BASE_URL}/projects/{project_id}", json=payload_update)
            #assert update_res.status_code in [200, 204]

            # Delete
            delete_res = requests.delete(f"{BASE_URL}/projects/{project_id}")
            #assert delete_res.status_code in [200, 204]

            elapsed = time.time() - start
            times.append(elapsed)
            status_tracker.append("PASS")

        except Exception as e:
            print(f" Sequence {i} failed: {e}")
            times.append(None)
            status_tracker.append("FAIL")

    successful = [t for t in times if t is not None]
    avg_time = sum(successful) / len(successful) if successful else None

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().available / (1024 ** 2)

    print(f"\n Finished batch. Avg time per sequence: {avg_time:.4f}s")
    print(f" CPU: {cpu}%, Memory: {mem:.2f} MB")

    return times, status_tracker, cpu, mem


def write_results(operation, times, statuses, cpu, memory, batch_size):
    filename = f"{operation}_batch_{batch_size}_results.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Request#", "Response Time (s)", "Status Code"])
        for i, (t, s) in enumerate(zip(times, statuses)):
            writer.writerow([i, t, s])
        writer.writerow([])
        writer.writerow(["CPU (%)", "Memory (MB)"])
        writer.writerow([cpu, memory])
    print(f" Results saved to: {filename}")


def run(sequence = False):
    batch_sizes = [15000, 20000, 50000]
    if not sequence:
        operations = ["create", "update", "delete"]

        for op in operations:
            for size in batch_sizes:
                times, statuses, cpu, memory = send_requests(op, size)
                write_results(op, times, statuses, cpu, memory, size)
    else:
        for size in batch_sizes:
            times, statuses, cpu, memory = create_update_delete_sequence(size)
            write_results("CUD", times, statuses, cpu, memory, size)


def main():
    sequence = False
    run(sequence)

if __name__ == "__main__":
    main()
