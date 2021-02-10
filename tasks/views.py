from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import Priority, TodoItem, Category
from datetime import datetime
from django.views.decorators.cache import cache_page

@cache_page(300)
def index(request):
    from django.db.models import Count

    counts_cat = Category.objects.annotate(total_tasks=Count('todoitem')).order_by("-total_tasks")
    counts_cat = {c.name: c.total_tasks for c in counts_cat}

    counts_prior = Priority.objects.annotate(total_tasks=Count('priority')).order_by("-total_tasks")
    counts_prior = {c.name: c.total_tasks for c in counts_prior}

    now_date = datetime.now().strftime('%d-%m-%Y %H:%M')

    context = {'counts_cat': counts_cat, 'counts_prior': counts_prior, 'date': now_date}
    return render(request, "tasks/index.html", context)

def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )

class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tasks = self.get_queryset()
        categories = {}
        for t in user_tasks:
            for cat in t.category.all():
                categories.setdefault(cat, []).append(t)
        context["categories"] = categories
        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"
