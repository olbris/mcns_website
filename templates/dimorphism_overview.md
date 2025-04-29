---
title: Dimorphism
hide:
  - navigation
  - toc
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

=== "By Supertype"

    _TODO_

=== "By Clone/Synonym"

    _TODO_

=== "By Hemilineage"

    _EXPLANATION/CAVEATS HERE_

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
                  <a href="{{ record.url }}" target="_blank">Open in Neuroglancer</a>
                </p>
            </div>
        </div>

        <h4 style="margin-top: 1.5em;">Cell Types</h4>

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in record.types %}
          - ![](thumbnails/{{ row.type_file }}.png)[{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md) ({{ row.type_type }})
        {% endfor %}
        </div>

    {% endfor %}


[^1]: Dorkenwald et al., Nature (2024); Schlegel et al., Nature (2024)