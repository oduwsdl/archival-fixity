# Archival Fixity

* We used these Python/shell scripts as part of evaluating the two approaches (Atomic and Block) that can be used to verify the fixity of archived web pages (or mementos). Both approaches are introduced in the ACM/IEEE Joint Conference on Digital Libraries (JCDL 2019) full paper. (An extended version of the JCDL paper is available as a technical report https://arxiv.org/abs/1905.12565).
* The scripts are mainly used to:
  * Generate fixity information of mementos
  * Publish the fixity information online at the Archival Fixity server https://github.com/oduwsdl/manifest
  * Disseminate the published fixity information to multiple archives
  * Verify the fixity of mementos
* Examples will be added soon to show how to generate, publish, and disseminate fixity information using both Atomic and Block approaches. We will also provide examples that illustrate how the archived fixity information can be used to verify the fixity of mementos.

## Citing Project

A publication related to this project appeared in the proceedings of JCDL 2019 ([Read the PDF](https://arxiv.org/pdf/1905.12565.pdf)). Please cite it as below:

> Mohamed Aturban, Sawood Alam, Michael L. Nelson, and Michele C. Weigle. __Archive Assisted Archival Fixity Verification Framework__. In _Proceedings of the 19th ACM/IEEE-CS on Joint Conference on Digital Libraries, JCDL 2019_, pp. 162-171, Urbana-Champaign, IL, USA, June 2019.

```latex
@inproceedings{jcdl-2019:aturban:fixityblocks,
  author    = {Mohamed Aturban and
               Sawood Alam and
               Michael L. Nelson and
               Michele C. Weigle},
  title     = {{Archive Assisted Archival Fixity Verification Framework}},
  booktitle = {Proceedings of the 19th ACM/IEEE-CS Joint Conference on Digital Libraries},
  series    = {JCDL '19},
  pages     = {162--171},
  numpages  = {10},
  year      = {2019},
  month     = {jun},
  url       = {https://doi.org/10.1109/JCDL.2019.00032},
  doi       = {10.1109/JCDL.2019.00032},
  isbn      = {978-1-7281-1547-4},
  publisher = {IEEE},
  location  = {Urbana-Champaign, IL, USA}
}
```
