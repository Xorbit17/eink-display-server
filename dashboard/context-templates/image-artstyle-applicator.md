# Image art style application

You will only output a generated image.
The output aspect ratio is {{aspect_ratio}}.
The output image will be further processed for display on an e-ink screen.
{% if palette %}You will use the palette shown in one of the included images. It was chosen with the art style in mind as well as optimal display for e-ink screens.{% endif %}

Purpose:
These images are generated purely for fun and artistic exploration.
The goal is to make people smile and laugh when they see themselves or their friends stylized in different artistic looks on a personal photo frame.
This is not for political or commercial use, but simply playful home display.

Please make sure not to generate any of these qualities:
* Blurriness unless the art style requires it
* Large areas covered by gradients, prefer a lower number of shades
* Lines with heavy antialiasing or blurry edges
* Extremely fine details in the range of 5 pixels or smaller
* Extra limbs for humans or animals
{% if palette %}* Keep to the provided color palette as strictly as possible{% endif %}

When the subject is a child make sure to preserve the child like features of the person.
The same is true for adults and older people.

These are the specific instructions for type of content {{content_type}}:

---

{{content_type_prompt|safe}}

{% if generation_context %}---

These are the specific instructions from the art style director.

```
{{generation_context|safe}}
```

{% endif %}
---

{{content_type_prompt|safe}}

---

This are the specific instructions for the art style {{art_style}}:

---

{{artstyle_prompt|safe}}

---

