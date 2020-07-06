### usage on local

#### build container

`sh ./build.sh`

built `sm-w2v-similar` container


#### train

put train data file
to `./local_test/test_dir/input/data/train/train.txt`

ex)

```
word1 word2 word3
word1 word4
...
```

`cd local_test`

`sh ./train_local.sh sm-w2v-similar`

if training completed, output model files in `./local_test/test_dir/model`


#### test for predict server

start predict server.

`cd local_test`

`sh ./serve_local.sh sm-w2v-similar`

request to predict server.
post `payload.csv` data.

`sh ./predict.sh`


### how to deploy

#### 1. push to ECR

`sh ./build_and_push.sh sm-w2v-similar`

build `sm-w2v-similar` container
and push container to `${account}.dkr.ecr.${region}.amazonaws.com/sm-w2v-similar:latest`

#### 2. deploy and create endpoint

need to install `boto3` package

`pip install boto3`

and setup AWS credentials. refer https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

`python deploy_endpoint.py`

### folder structure

#### w2v_similar

scripts copy into custom container.

#### local_test

for test train&predict on local

