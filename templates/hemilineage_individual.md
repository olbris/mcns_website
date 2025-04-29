---
title: {{ meta.type }}
hide:
  - toc
  - navigation
---

<!-- this links the font-awesome stylesheet v4 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

# Hemilineage "{{ meta.hemilineage }}"


<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;">
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); flex: .4; min-width: 300px;">
        <div style="width: 100%; display: table;">
            <!-- These are the individual properties for the summary -->
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Superclass(es): </div>
                <div style="display: table-cell;"> {{ meta.superclass }} </div>
            </div>
            <hr style="margin: 0;">
            {% if meta.synonyms != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Synonyms: </div>
                <div style="display: table-cell;"> {{ meta.synonyms }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Type Counts</b> (left|right): </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Male: </div>
                <div style="display: table-cell;"> {{ meta.n_types_mcnsl }} | {{ meta.n_types_mcnsr }}</div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Female: </div>
                <div style="display: table-cell;"> {{ meta.n_types_fwl }} | {{ meta.n_types_fwr }}</div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Neuron Counts</b> (left|right): </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Male: </div>
                <div style="display: table-cell;"> {{ meta.n_mcnsl }} | {{ meta.n_mcnsr }}</div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Female: </div>
                <div style="display: table-cell;"> {{ meta.n_fwl }} | {{ meta.n_fwr }}</div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Consensus NTs: </div>
                <div style="display: table-cell;"> {{ meta.consensusNt }} </div>
            </div>
            <hr style="margin: 0;">
            {% if meta.itoleeHl != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;">Ito & Lee nomenclature: </div>
                <div style="display: table-cell;"> {{ meta.itoleeHl }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.trumanHl != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;">Truman nomenclature: </div>
                <div style="display: table-cell;"> {{ meta.trumanHl }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.somaNeuromere != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Soma Neuromere(s): </div>
                <div style="display: table-cell;"> {{ meta.somaNeuromere }} </div>
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




