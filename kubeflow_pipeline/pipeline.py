import os

import kfp
import kfp.components as comp
from kfp import dsl
from kubernetes import client as k8s_client

@dsl.pipeline(
    name="mnist using arcface",
    description="CT pipeline"
)

def mnist_pipeline():
    data_0 = dsl.ContainerOp(
        name="load & preprocess data pipeline",
        image="byeongjokim/mnist-pre-data:latest",
    )\
    .add_volume(k8s_client.V1Volume(name='data', host_path=k8s_client.V1HostPathVolumeSource(path='/data')))\
    .add_volume_mount(k8s_client.V1VolumeMount(mount_path='/data', name='data'))\
    .set_display_name('collect & preprocess data')


    data_1 = dsl.ContainerOp(
        name="validate data pipeline",
        image="byeongjokim/mnist-val-data:latest",
    )\
    .add_volume(k8s_client.V1Volume(name='data', host_path=k8s_client.V1HostPathVolumeSource(path='/data')))\
    .add_volume_mount(k8s_client.V1VolumeMount(mount_path='/data', name='data'))\
    .set_display_name('validate data')\
    .after(data_0)

    train_model = dsl.ContainerOp(
        name="train embedding model",
        image="byeongjokim/mnist-train-model:latest"
    )\
    .add_volume(k8s_client.V1Volume(name='data', host_path=k8s_client.V1HostPathVolumeSource(path='/data')))\
    .add_volume_mount(k8s_client.V1VolumeMount(mount_path='/data', name='data'))\
    .add_volume(k8s_client.V1Volume(name='model', host_path=k8s_client.V1HostPathVolumeSource(path='/model')))\
    .add_volume_mount(k8s_client.V1VolumeMount(mount_path='/model', name='model'))\
    .set_display_name('train model')\
    .after(data_1)


    # embedding = dsl.ContainerOp(
    #     name="embedding data using embedding model",
    #     image="byeongjokim/mnist-embedding:latest"
    # )\
    # .set_display_name('embedding')

    # train_faiss = dsl.ContainerOp(
    #     name="train faiss",
    #     image="byeongjokim/mnist-train-faiss:latest"
    # )\
    # .set_display_name('train faiss')

    # analysis = dsl.ContainerOp(
    #     name="analysis total",
    #     image="byeongjokim/mnist-analysis:latest"
    # )\
    # .set_display_name('analysis')

    # \
    # .add_volume(k8s_client.V1Volume(name='model', host_path=k8s_client.V1HostPathVolumeSource(path='/model')))\
    # .add_volume_mount(k8s_client.V1VolumeMount(mount_path='/model', name='model'))

if __name__=="__main__":
    host = "http://220.116.228.93:8080/pipeline"
    namespace = "kbj"
    pipeline_package_path = "pipeline.zip"
    kfp.compiler.Compiler().compile(mnist_pipeline, pipeline_package_path)

    client = kfp.Client(host=host, namespace=namespace)
    pipeline_file = os.path.join(pipeline_package_path)
    pipeline = client.pipeline_uploads.upload_pipeline(pipeline_file)