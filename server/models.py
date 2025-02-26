from django.db import models
from django.forms import model_to_dict
from django.contrib.auth import models as auth_models
from django.utils import timezone

User = auth_models.User

def create_dict(model: models.Model) -> dict:
    """
    Recursively creates a dictionary based on the supplied model and all its foreign relationships.
    """
    d: dict = model_to_dict(model)
    model_type: type = type(model)
    d["model_type"] = model_type.__name__

    if model_type == InstancedEntity:
        d["entity"] = create_dict(model.entity)

    elif model_type == Actor:
        d["instanced_entity"] = create_dict(model.instanced_entity)
        # Purposefully don't include user information here.
#TICTACTOE -----------------------------
    elif model_type == TicTacToeGame:
        d["instanced_entity"] = create_dict(model.instanced_entity)
        if model.is_active:
            d["is_active"] = create_dict(model.is_active)
    elif model_type == TicTacToeSpot:
        d["instanced_entity"] = create_dict(model.instanced_entity)
        if model.occupied_by:
            d["occupied_by"] = create_dict(model.occupied_by)
#TICTACTOE------------------------------
    return d

def get_delta_dict(model_dict_before: dict, model_dict_after: dict) -> dict:
    """
    Returns a dictionary containing all differences between the supplied model dicts
    (except for the ID and Model Type).
    """
    delta: dict = {}

    for k in model_dict_before.keys() & model_dict_after.keys():  # Intersection of keysets
        v_before = model_dict_before[k]
        v_after = model_dict_after[k]

        if k in ("id", "model_type"):
            delta[k] = v_after
        if v_before == v_after:
            continue

        if not isinstance(v_before, dict):
            delta[k] = v_after
        else:
            delta[k] = get_delta_dict(v_before, v_after)

    return delta

class Entity(models.Model):
    name = models.CharField(max_length=100)

class InstancedEntity(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

class Actor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instanced_entity = models.OneToOneField(InstancedEntity, on_delete=models.CASCADE)
    avatar_id = models.IntegerField(default=0)
#TICTACTOE -----------------------------
class TicTacToeSpot(models.Model):
    spot_number = models.IntegerField() # Either 1 or 2
    instanced_entity = models.OneToOneField(InstancedEntity, on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)
    occupied_by = models.ForeignKey(Actor, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'spot'

class TicTacToeGame(models.Model):
    game_number = models.IntegerField()
    instanced_entity = models.OneToOneField(InstancedEntity, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'game'
#TICTACTOE -----------------------------