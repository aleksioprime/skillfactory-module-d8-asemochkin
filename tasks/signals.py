from django.db.models.signals import m2m_changed, post_delete, pre_delete, post_save
from django.dispatch import receiver
from tasks.models import TodoItem, Priority


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(instance, action, **kwargs):
    if action == "post_add":
        for cat in instance.category.all():
            cat.todos_count += 1
            cat.save()

    if action == "pre_remove":
        for cat in instance.category.all():
            cat.todos_count -= 1
            cat.save()

@receiver(pre_delete, sender=TodoItem)
def task_cats_delete(instance, **kwargs):
    for cat in instance.category.all():
        cat.todos_count -= 1
        cat.save()

@receiver(post_delete, sender=TodoItem)
@receiver(post_save, sender=TodoItem)
def task_prior_count(**kwargs):
    for pr in Priority.objects.all():
        pr.todos_count = TodoItem.objects.filter(prior=pr).all().count()
        pr.save()
