FROM duckietown/aido2-base-python3:z2

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .


ENTRYPOINT ["python3", "dummy_simulator.py"]

