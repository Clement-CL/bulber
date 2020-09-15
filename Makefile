### GCP configuration - - - - - - - - - - - - - - - - - - -

# /!\ you should fill these according to your account

### GCP Project - - - - - - - - - - - - - - - - - - - - - -

PROJECT_NAME=bulber

### GCP Storage - - - - - - - - - - - - - - - - - - - - - -

BUCKET_NAME=bulber_bucket_1

##### Data  - - - - - - - - - - - - - - - - - - - - - - - -

# not required here

##### Training  - - - - - - - - - - - - - - - - - - - - - -

# will store the packages uploaded to GCP for the training
BUCKET_TRAINING_FOLDER = trainings

### GCP AI Platform - - - - - - - - - - - - - - - - - - - -

REGION=europe-west1

PYTHON_VERSION=3.7
FRAMEWORK=tensorflow
RUNTIME_VERSION=1.15

##### Package params  - - - - - - - - - - - - - - - - - - -

PACKAGE_NAME=bulber
FILENAME=trainer

##### Job - - - - - - - - - - - - - - - - - - - - - - - - -

JOB_NAME=bulber_training_model_$(shell date +'%Y%m%d_%H%M%S')

##### Machine Type - - - - - - - - - - - - - - - - - - - - - - - - -
MACHINE_TYPE=n1-standard-16


run_locally:
	@python -m ${PACKAGE_NAME}.${FILENAME}

gcp_submit_training:
	gcloud ai-platform jobs submit training ${JOB_NAME} \
		--job-dir gs://${BUCKET_NAME}/${BUCKET_TRAINING_FOLDER} \
		--package-path ${PACKAGE_NAME} \
		--module-name ${PACKAGE_NAME}.${FILENAME} \
		--python-version=${PYTHON_VERSION} \
		--runtime-version=${RUNTIME_VERSION} \
		--region ${REGION} \
		--scale-tier CUSTOM \
		--master-machine-type ${MACHINE_TYPE}

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ __pycache__
	@rm -fr build dist *.dist-info *.egg-info
	@rm -fr */*.pyc
	@rm model.joblib
