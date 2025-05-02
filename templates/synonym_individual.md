---
title: {{ meta.name }}
hide:
  - toc
  - navigation
  - tags
tags:
   - {{ meta.name }}
   {% for pub in meta.publications %}
   - {{ pub }}
   {% endfor %}
---

<!-- this links the font-awesome stylesheet v4 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

# Synonym "{{ meta.name }}"

<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;">
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); flex: .4; min-width: 300px;">
        <div style="width: 100%; display: table;">
            <!-- These are the individual properties for the summary -->
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Publication</b>(s): </div>
                <div style="display: table-cell;"> {{ meta.author_year_str }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Neurons in Male</b>: </div>
                <div style="display: table-cell;"> {{ meta.n_mcns }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Neurons in Female</b>: </div>
                <div style="display: table-cell;"> {{ meta.n_fw }} </div>
            </div>
            <hr style="margin: 0;">
            {% if meta.itoleeHl != "N/A" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Hemilineage</b>(s) (Ito & Lee): </div>
                <div style="display: table-cell;"> {% for lin in meta.itoleeHl %}<a href="../../hemilineages/{{ lin }}">{{ lin }} </a>{% endfor %} </div>
            </div>
            <hr style="margin: 0;">
            {% elif meta.ito_lee_hemilineage != "N/A" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Hemilineage</b>(s) (Ito & Lee): </div>
                <div style="display: table-cell;"> <a href="../../hemilineages/{{ meta.ito_lee_hemilineage }}">{{ meta.ito_lee_hemilineage }}</a> </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.trumanHl != "N/A" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Hemilineage</b>(s) (Truman): </div>
                <div style="display: table-cell;"> <a href="../../hemilineages/{{ meta.trumanHl }}">{{ meta.trumanHl }}</a> </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
        </div>
    </div>
    <!-- This is the container for the neuroglancer frame -->
    <div style="text-align: center; flex: .7; min-width: 300px;">
        <div style="text-align: center;">
            <iframe src="{{ meta.url }}" width="100%" height="500px" style="border:none;"></iframe>
            <br>
            <a href="{{ meta.url }}" target="_blank">Open in new tab</a>
        </div>
    </div>
</div>

### Dimorphic Cell Types

<div class="grid cards" style="text-align: center;" markdown>
{% for row in meta.types %}
  - ![](../../thumbnails/{{ row.type_file }}.png)[{{ row.label }}](../../summary_types/{{ row.type_file }}) ({{ row.dimorphism_type }})
{% endfor %}
</div>




