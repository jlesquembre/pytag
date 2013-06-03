=================
Supported formats
=================


Ogg based
---------

+------------+-----------+------+-------+
|            | Extension | Read | Write |
+============+===========+======+=======+
| Ogg Vorbis |   .ogg    | Yes  | Yes   |
+------------+-----------+------+-------+

Mp3
---

+------------+------+-------+
|            | Read | Write |
+============+======+=======+
| ID3v1.1    | Yes  | No    |
+------------+------+-------+
| ID3v2.2    | Yes  | No    |
+------------+------+-------+
| ID3v2.3    | Yes  | No    |
+------------+------+-------+
| ID3v2.4    | Yes  | Yes   |
+------------+------+-------+

.. note::

    Anyway, is possible to save the metadata in any mp3 file, the tags are just
    replaced with the last ID3 version (2.4 currently)
