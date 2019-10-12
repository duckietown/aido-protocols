FROM duckietown/aido3-base-python3:daffy

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .


ENTRYPOINT ["python3", "dummy_simulator.py"]

