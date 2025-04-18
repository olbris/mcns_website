---
title: {{ meta.type }}
hide:
  - toc
  - navigation
---

# {{ meta.type }}

##### Superclass: {{ meta.superclass }}; Cell Class: {{ meta.class }}

{% if meta.synonyms != "None" %}
##### Synonyms
{{ meta.synonyms }}
{% endif %}

{% if meta.matchingNotes != "None" %}
##### Matching Notes
{{ meta.synonyms }}
{% endif %}

## Visualization

<div style="text-align: center;">
    <iframe src="{{ meta.url }}" width="90%" height="500px" style="border:none;"></iframe>
</div>

## Partners

<embed type="text/html", src="{{ meta.graph_file }}", width="100%", height="500px" style="border:none;"></embed>



