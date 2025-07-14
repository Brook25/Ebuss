from rest_framework import serializers

# override the get_links method in sub classes
#+ and return None since
#+ some models don't need url links
#+ check serializers file for product model


class BaseSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def update(self, instance, **kwargs):
        
        for k, v in self.validated_data.items():
            setattr(instance, k, v)
        instance.save()

        return instance
    
    def bulk_create(self, kwargs):
        model = self.Meta.model
        return model.objects.bulk_create(model(**data) for data in self.validated_data)
