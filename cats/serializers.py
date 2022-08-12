import datetime as dt

import webcolors
from rest_framework import serializers

from .models import CHOICES, Achievement, AchievementCat, Cat, Owner


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    # если в модели изменится __str__(), то изменится поле owner
    # (т.к. StringRelatedField) в ответах API.
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
#    color = Hex2NameColor()
    color = serializers.ChoiceField(choices=CHOICES)
    # достаточно здесь или в модели параллельно надо тоже choises?

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements',
                  'age')

    def get_age(self, obj):
        # хорошо не перегружать этот метод тяжёлыми операциями.
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        achievements = validated_data.pop('achievements')
        cat = Cat.objects.create(**validated_data)
        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement)
        # что за конструкция, где status?
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat)
        return cat


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)
    # если в модели изменится __str__(), то изменится поле cats
    # (т.к. StringRelatedField) в ответах API.

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')


class CatListSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color')
