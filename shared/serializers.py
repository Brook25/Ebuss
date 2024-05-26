

# override the get_links method in sub classes
#+ and return None since
#+ some models don't need url links
#+ check serializers file for product model

class BaseSerializer(serializers.HyperLinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        fields = kwargs.pop('fields', None)
        extra_kwargs = kwargs.pop('extra_kwargs')
        super().__init__(*args, **kwargs)

        if model and fields:
            self.Meta.model = model
            self.Meta.fields = fields
            self.Meta.extra_kwargs = extra_kwargs

    def to_representation(self, obj):

        representation = super().to_representation(obj)
        view_name = self.extra_kwargs.get('url', {}).get('view_name', None)

        if view_name:
            representation['url'] = reverse(view_name, kwargs={'id': obj.id})



    class Meta:
        model = None
        fields = None
