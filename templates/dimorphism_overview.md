---
title: Dimorphism
hide:
  - navigation
  - toc
---

# :material-gender-male-female: Dimorphism Overview

By comparing the male CNS to the female "FlyWire" connectome, we identified a number of sexually dimorphic neurons.

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


