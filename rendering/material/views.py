from django.shortcuts import render

from .models import Pattern, Finish, Nature, ColorMatch, ColorMatchingChart


# from django.views.generic import TemplateView, ListView, DetailView
# Create your views here.

def index(request, nature_id=0, pattern_id=0):
    context = {
        'nav_active': 'material',
        'selected': {},
        'natures': Nature.objects.exclude(name='none')  # .exclude(finishes__count=0)
    }
    if nature_id:  # selected nature => we can show patterns, and if
        context['selected']['nature'] = Nature.objects.get(pk=nature_id)
        context['patterns'] = Pattern.objects.filter(nature=context['selected']['nature'])
        if len(list(context['patterns'])) == 1:
            pattern_id = context['patterns'].first().id  # select pattern if it one in nature

    if pattern_id:
        context['patterns'] = Pattern.objects.filter(pk=pattern_id)
        context['selected']['pattern'] = Pattern.objects.get(pk=pattern_id)
        context['selected']['nature'] = context['selected']['pattern'].nature
        context['finishes'] = Finish.objects.filter(pattern_id=pattern_id).exclude(archive=True)

    return render(request, 'material/index.html', context)


def finish_details(request, pk):
    return render(request, 'material/details.html', {'m': Finish.objects.get(pk=pk),
                                           'nav_active': 'material'})

def pattern_details(request, pk):
    pass
    #return "pattern_details"
    # return render(request, 'index.html', {'finishes': Finish.objects.filter(pattern_id=id),
    #                                       'nav_active': 'material'})

def nature_details(request, pk):
    pass
    # if nature == 'fabric':
    #     context = {'natures': Nature.objects.annotate(Count('pattern__texture'))}
    #     ps_all = Pattern.objects.filter(nature__name=nature).annotate(Count('texture'))
    #     context['t_selected'] = id
    #     if len(ps_all) > 1:
    #         rows = []
    #         ROWSIZE = 8
    #         ps = [p for p in ps_all if p.name[-10:] == 'by_Kvadrat']
    #         for k in range(len(ps)//ROWSIZE):
    #             rows.append(ps[k*ROWSIZE:(k+1)*ROWSIZE])
    #         if len(ps) % ROWSIZE:
    #             rows.append(ps[(len(ps)//ROWSIZE)*ROWSIZE:])
    #         ROWSIZE = 7
    #         ps = [p for p in ps_all if not p.name[-10:] == 'by_Kvadrat']
    #         for k in range(len(ps) // ROWSIZE):
    #             rows.append(ps[k * ROWSIZE:(k + 1) * ROWSIZE])
    #         if len(ps) % ROWSIZE:
    #             rows.append(ps[(len(ps) // ROWSIZE) * ROWSIZE:])
    #
    #
    #         context['patterns'] = rows
    #         context['patterns_count'] = len(ps_all)
    #
    #     return render(request, 'index.html', context)
    # else:
    #     return render(request, 'index.html', {'textures': Finish.objects.filter(pattern__nature__id=nature_id),
    #                                               'nav_active': 'material'})

def colorchart_index(request):
    return ColorMatchingChart.objects.all()


def colorchart(request, pk):
    matches = ColorMatch.objects.filter(chart=pk)
    textures = []
    for m in matches:
        textures.append({'finish': m.finish, 'suited': [Finish.objects.get(pk=i) for i in m.suited.split(',')], })
    return render(request, 'colorchart.html', {'name': ColorMatchingChart.objects.get(pk=pk).name,
                                               'matches': textures,
                                               'nav_active': 'material'})
