---
title: Dimorphism
hide:
  - navigation
  - toc
  - tags
---

# :material-gender-male-female: Dimorphism Overview

By comparing the male CNS to the previously published female "FlyWire" connectome[^1], we identified a number of sexually dimorphic neurons.
Below you can browse the list of dimorphic and sex-specific cell types grouped by either their cell types, their light-level clone, their
hemi-lineage, or their synonym.

=== "By Terminal Type"

    Here we present the list of dimorphic neurons grouped by their terminal type.

    === "Sexually dimorphic cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in dimorphic_types %}
          - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md)
        {% endfor %}
        </div>

    === "Male-specific cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in male_types %}
          - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md)
        {% endfor %}
        </div>

    === "Female-specific cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in female_types %}
          - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md)
        {% endfor %}
        </div>

=== "By Clone/Synonym"

    _TODO_

=== "By Brain Region"

    This section represents dimorphism in the context of the brain regions they are located in. Types are listed under a given brain region
    if they have more than 10% of their in- or outputs (by number of synapses) in that region. Only regions with at least one dimorphic type are shown.

    === "Brain"

        {% for key, record in regions.CentralBrain.items() %}
        ??? Abstract "{{ key }}"

            <div class="grid cards" style="text-align: center;" markdown>
            {% for row in record.types %}
              - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md) ({{ row.dimorphism_type }})
            {% endfor %}
            </div>

        {% endfor %}

    === "Ventral Nerve Cord"

        {% for key, record in regions.VNC.items() %}
        ??? Abstract "{{ key }}"

            <div class="grid cards" style="text-align: center;" markdown>
            {% for row in record.types %}
              - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md) ({{ row.dimorphism_type }})
            {% endfor %}
            </div>

        {% endfor %}

    === "Visual System"

        {% for key, record in regions.Optic.items() %}
        ??? Abstract "{{ key }}"

            <div class="grid cards" style="text-align: center;" markdown>
            {% for row in record.types %}
              - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md) ({{ row.dimorphism_type }})
            {% endfor %}
            </div>

        {% endfor %}

=== "By Supertype"

    Supertypes are groups of neurons that share morphological features. They typically combine of 3-4 terminal cell types but can be larger - e.g. when they contain types with
    morphologies that only gradually differ from each other. Only supertypes with at least one dimorphic or sex-specific type are shown.

    <div class="grid cards" style="text-align: center;" markdown>
    {% for row in supertypes %}
      - ![](thumbnails/{{ row.name }}.png)[{{ row.name }}](supertypes/{{ row.name }}.md) ({{ row.dimorphism_types }})
    {% endfor %}
    </div>


=== "By Hemilineage"

    This section groups dimorphic terminal cell types by the developmental hemilineage they originate from. The expression of the _fruitless_ (_fru+_) and _doublesex_ (_dsx+_) genes was
    established by comparing neuron morphologies to light-level clones. Please note that not necessarily all neurons in a hemilineage are _fruitless_- or _doublesex_-positive.
    Only hemilineages with at least one dimorphic type are shown.

    {% for record in hemilineages %}
    ??? Abstract "{{ record.name }} ({{ record.fru_dsx }})"

        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;">
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); flex: .9; min-width: 300px;">
                <div style="width: 100%; display: table;">
                    <!-- These are the individual properties for the summary -->
                    <div style="display: table-row">
                        <div style="width: 50%; display: table-cell;"> <b>Counts in Male</b> (left|right): </div>
                        <div style="display: table-cell;"> {{ record.n_mcnsl }} | {{ record.n_mcnsr }}</div>
                    </div>
                    <hr style="margin: 0;">
                    <div style="display: table-row">
                        <div style="width: 50%; display: table-cell;"> <b>Counts in Female</b> (left|right): </div>
                        <div style="display: table-cell;"> {{ record.n_fwl }} | {{ record.n_fwr }}</div>
                    </div>
                </div>
                <!-- Links to NeuroGlancer (note also that we're adding a spacer)  -->
                <p style="margin-top:.2cm;">
                  <a href="{{ record.url }}" target="_blank">Show hemilineage in Neuroglancer</a>
                </p>
            </div>
        </div>

        <h4 style="margin-top: 1.5em;">Cell Types</h4>

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in record.types %}
          - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md) ({{ row.dimorphism_type }})
        {% endfor %}
        </div>

    {% endfor %}


[^1]: Dorkenwald et al., Nature (2024); Schlegel et al., Nature (2024)