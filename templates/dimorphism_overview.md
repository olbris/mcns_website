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
          - [{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md)
        {% endfor %}
        </div>

    === "Male-specific cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in male_types %}
          - [{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md)
        {% endfor %}
        </div>

    === "Female-specific cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in female_types %}
          - [{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md)
        {% endfor %}
        </div>

=== "By Supertype"

    _TODO_

=== "By Clone"

    _TODO_

=== "By Hemilineage"

    {% for record in hemilineages %}
    ??? Abstract "{{ record.name }}"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in record.types %}
          - [{{ row.type }}]({{ summary_types_dir }}/{{ row.type_file }}.md) ({{ row.type_type }})
        {% endfor %}
        </div>

    {% endfor %}

=== "By Synonym"

    _TODO_


[^1]: Dorkenwald et al., Nature (2024); Schlegel et al., Nature (2024)