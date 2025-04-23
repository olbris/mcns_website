---
title: Dimorphism
hide:
  - navigation
  - toc
---

# :material-gender-male-female: Dimorphism Overview

By comparing the male CNS to the previously published female "FlyWire" connectome[^1], we identified a number of sexually dimorphic neurons.
Here we present a summary of these types and their properties.

=== "By Terminal Type"

    _Explanation here_

    === "Sexually dimorphic cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in dimorphic_types %}
          - [{{row.type}}]({{row.type}}.md)
        {% endfor %}
        </div>

    === "Male-specific cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in male_types %}
          - [{{row.type}}]({{row.type}}.md)
        {% endfor %}
        </div>

    === "Female-specific cell types"

        <div class="grid cards" style="text-align: center;" markdown>
        {% for row in female_types %}
          - [{{row.type}}]({{row.type}}.md)
        {% endfor %}
        </div>

=== "By Clone"

    _TODO_

=== "By Hemilineage"

    _TODO_

=== "By Synonym"

    _TODO_


[^1]: Dorkenwald et al., Nature (2024); Schlegel et al., Nature (2024)