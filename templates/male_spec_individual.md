---
title: {{ meta.type }}
hide:
  - toc
  - navigation
---

<!-- this links the font-awesome stylesheet v4 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

# Male-specific Cell Type "{{ meta.type }}" [:octicons-link-external-24:{ .small-icon }]( {{ meta.neuprint_url }} "View on NeuPrint"){target="_blank"}


<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;">
    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); flex: .4; min-width: 300px;">
        <div style="width: 100%; display: table;">
            <!-- These are the individual properties for the summary -->
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Superclass: </div>
                <div style="display: table-cell;"> {{ meta.superclass }} </div>
            </div>
            <hr style="margin: 0;">
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Cell Class: </div>
                <div style="display: table-cell;"> {{ meta.class }} </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Supertype: </div>
                <div style="display: table-cell;"> <a href="../supertypes/{{ meta.supertype }}">{{ meta.supertype }}</a> </div>
            </div>
            <hr style="margin: 0;">
            {% if meta.mancType != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> MANC Type: </div>
                <div style="display: table-cell;"> {{ meta.mancType }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.synonyms != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Synonyms: </div>
                <div style="display: table-cell;"> {{ meta.synonyms }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.matchingNotes != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Matching Notes: </div>
                <div style="display: table-cell;"> {{ meta.matchingNotes }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Counts</b> (left|right): </div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;">&nbsp &nbsp Male: </div>
                <div style="display: table-cell;"> {{ meta.n_mcnsl }} | {{ meta.n_mcnsr }}</div>
            </div>
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Consensus NT: </div>
                <div style="display: table-cell;"> {{ meta.consensusNt }} </div>
            </div>
            <hr style="margin: 0;">
            {% if meta.itoleeHl != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Hemilineage</b> (Ito & Lee): </div>
                <div style="display: table-cell;"> <a href="../hemilineages/{{ meta.itoleeHl }}">{{ meta.itoleeHl }}</a> </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.trumanHl != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell;"> <b>Hemilineage</b> (Truman): </div>
                <div style="display: table-cell;"> <a href="../hemilineages/{{ meta.trumanHl }}">{{ meta.trumanHl }}</a> </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.somaNeuromere != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> Soma Neuromere: </div>
                <div style="display: table-cell;"> {{ meta.somaNeuromere }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
            {% if meta.mcnsSerial != "None" %}
            <div style="display: table-row">
                <div style="width: 50%; display: table-cell; font-weight: bold;"> MCNS Serial: </div>
                <div style="display: table-cell;"> {{ meta.mcnsSerial }} </div>
            </div>
            <hr style="margin: 0;">
            {% endif %}
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
    <div style="position: relative; display: inline-block;">
        <button style="background-color: transparent; border: none; cursor: pointer; font-size: 16px; color: #0078D4;">&#x3F;</button>
        <div style="visibility: hidden; width: 200px; background-color: #f9f9f9; color: #333; text-align: center; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; bottom: 125%; left: 50%; transform: translateX(-50%); box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);">
            The graphs below show the 5 strongest up- and downstream partners for {{ meta.type}}. Click on the link icons to view the full connectivity in neuPrint.
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

<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
    <div style="flex: 1; min-width: 300px; text-align: center;">
        <h4>MaleCNS<a href="{{ meta.neuprint_conn_url }}" target="_blank"> <i class="fa fa-external-link"></i></a></h4>
        <embed type="text/html" src="{{ meta.graph_file_mcns_rel }}" width="100%" height="500px" style="border:none;"></embed>
    </div>
</div>



