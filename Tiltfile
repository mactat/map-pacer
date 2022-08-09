k8s_yaml('./agent/kubernetes.yaml')
k8s_resource('agent', port_forwards=8000,
             resource_deps=['deploy'])

local_resource(
    'deploy'
)

# Add a live_update rule to our docker_build
congrats = "🎉 Congrats, you ran a live_update! 🎉"
docker_build('example-python-image', '.', build_args={'flask_env': 'development'},
    live_update=[
        sync('./agent/', './agent/app'),
        run('cd /app && pip install -r requirements.txt',
            trigger='./requirements.txt'),

        # add a congrats message!
        run('sed -i "s/Hello cats!/{}/g" /app/templates/index.html'.
            format(congrats)),
])