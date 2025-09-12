---
title: {{ meta.type }}
hide:
  - toc
  - navigation
  - tags
tags:
   - {{ meta.type }}
   - {{ meta.mapping }}
   - {{ meta.hemibrain_type }}

---

<!-- this links the font-awesome stylesheet v4 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

# Female-specific Cell Type "{{ meta.type }}"


<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;">
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); flex: .4; min-width: 300px;">
        <div style="width: 100%; display: table;">
            <!-- These are the individual properties for the summary -->
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Superclass: </div>
                <div style="display: table-cell;"> {{ meta.super_class }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Cell Class: </div>
                <div style="display: table-cell;"> {{ meta.cell_class if meta.cell_class != "N/A" else "None" }} </div>
            </div>
            <hr style="margin: 0;">
            {% if meta.ito_lee_hemilineage != "N/A" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Hemilineage</b> (Ito & Lee): </div>
                <div style="display: table-cell;"> <a href="../../hemilineages/{{ meta.ito_lee_hemilineage }}">{{ meta.ito_lee_hemilineage }}</a> </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Supertype: </div>
                <div style="display: table-cell;"> <a href="../../supertypes/{{ meta.supertype }}">{{ meta.supertype }}</a> </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Across-brain Mapping
                    <div style="position: relative; display: inline-block;">
                        <button style="background-color: transparent; border: none; cursor: pointer; font-size: 16px; color: #0078D4;"><sup>&#x3F;</sup></button>
                        <div style="visibility: hidden; width: 200px; background-color: #f9f9f9; color: #333; text-align: center; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; bottom: 125%; left: 50%; transform: translateX(-50%); box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); font-weight: normal;">
                            A label mapping this groups of neurons between the male CNS and the FlyWire connectome, or between male CNS and the MANC dataset.
                            <div style="position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #f9f9f9 transparent transparent transparent;"></div>
                        </div>
                    </div>
                    :
                </div>
                <div style="display: table-cell;"> {{ meta.mapping }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Hemibrain Type: </div>
                <div style="display: table-cell;"> {{ meta.hemibrain_type }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Synonyms: </div>
                <div style="display: table-cell;"> {{ meta.synonyms_linked }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Matching Notes: </div>
                <div style="display: table-cell;"> {{ meta.matching_notes }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Counts</b> (left|right): </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Male: </div>
                <div style="display: table-cell;"> N/A | N/A </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Female: </div>
                <div style="display: table-cell;"> {{ meta.n_fwl }} | {{ meta.n_fwr }}</div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Neurotransmitter</b>(s): </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Male: </div>
                <div style="display: table-cell;"> N/A </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Female: </div>
                <div style="display: table-cell;"> {{ meta.top_nt }} </div>
            </div>
        </div>
        <!-- Links to neuPrint/Codex (note also that we're adding a spacer)  -->
        <!-- <p style="margin-top:3cm;">
            <a href="{{ meta.neuprint_url }}" target="_blank">See on neuPrint</a>
        </p> -->
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

<div style="display: flex; align-items: center; gap: 8px;">
    <h2>Connectivity</h2>
</div>

<!-- script for tooltips -->
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

<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
    <embed type="text/html" src="{{ meta.connections_file_rel }}" width="100%" height="4000px" style="border:none;"></embed>
</div>



