---
title: {{ meta.type }}
hide:
  - toc
  - navigation
---

# {{ meta.type }}


<!-- ##### Superclass: {{ meta.superclass }}; Cell Class: {{ meta.class }} -->

<!-- {% if meta.synonyms != "None" %}
##### Synonyms
{{ meta.synonyms }}
{% endif %}

{% if meta.matchingNotes != "None" %}
##### Matching Notes
{{ meta.synonyms }}
{% endif %} -->

<div style="display: flex; justify-content: space-between; gap: 20px;">
<div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); width:50%">
    <div style="width: 100%; display: table;">
        <div style="display: table-row">
            <div style="width: 30%; display: table-cell; font-weight: bold;"> Superclass: </div>
            <div style="display: table-cell;"> {{ meta.superclass }} </div>
        </div>
        <div style="display: table-row">
            <div style="width: 30%; display: table-cell; font-weight: bold;"> FlyWire Type: </div>
            <div style="display: table-cell;"> {{ meta.flywireType }} </div>
        </div>
        {% if meta.synonyms != "None" %}
        <div style="display: table-row">
            <div style="width: 30%; display: table-cell; font-weight: bold;"> Synonyms: </div>
            <div style="display: table-cell;"> {{ meta.synonyms }} </div>
        </div>
        {% endif %}
        {% if meta.matchingNotes != "None" %}
        <div style="display: table-row">
            <div style="width: 30%; display: table-cell; font-weight: bold;"> Matching Notes: </div>
            <div style="display: table-cell;"> {{ meta.matchingNotes }} </div>
        </div>
        {% endif %}
        <div style="display: table-row">
            <div style="width: 30%; display: table-cell; font-weight: bold;"> ... </div>
            <div style="display: table-cell;"> more properties here </div>
        </div>
    </div>
</div>

<!-- Other things to add: number of neurons per side per sex, flywire type/hemibrain type -->

<div style="text-align: center; width:60%">
<div style="text-align: center;">
    <iframe src="{{ meta.url }}" width="90%" height="500px" style="border:none;"></iframe>
    <br>
    <a href="{{ meta.url }}" target="_blank">Open in new tab</a>
</div>
</div>

</div>

<div style="display: flex; align-items: center; gap: 8px;">
    <h2>Connectivity</h2>
    <div style="position: relative; display: inline-block;">
        <button style="background-color: transparent; border: none; cursor: pointer; font-size: 16px; color: #0078D4;">&#x3F;</button>
        <div style="visibility: hidden; width: 200px; background-color: #f9f9f9; color: #333; text-align: center; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; bottom: 125%; left: 50%; transform: translateX(-50%); box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);">
            The graphs below show the 5 strongest up- and downstream partners for {{ meta.type}}.
            <div style="position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #f9f9f9 transparent transparent transparent;"></div>
        </div>
    </div>
</div>

<script>
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('mouseover', function() {
            this.nextElementSibling.style.visibility = 'visible';
        });
        button.addEventListener('mouseout', function() {
            this.nextElementSibling.style.visibility = 'hidden';
        });
    });
</script>

<div style="display: flex; justify-content: space-between; gap: 20px;">
    <div style="flex: 1; text-align: center;">
        <h4>MaleCNS</h4>
        <embed type="text/html" src="{{ meta.graph_file_mcns_rel }}" width="100%" height="500px" style="border:none;"></embed>
    </div>
    <div style="flex: 1; text-align: center;">
        <h4>female (FlyWire)</h4>
        <embed type="text/html" src="{{ meta.graph_file_fw_rel }}" width="100%" height="500px" style="border:none;"></embed>
    </div>
</div>



