# Defacto API

## Usage

```
pip3 install -r requirements.txt
```
Run the server
```
uvicorn main:app --reload
```
OpenAPI documentation & Endpoints can be accessed at
```
http://127.0.0.1:8000/docs
```

Setting up OpenSearch
```
POST /_plugins/_ml/model_groups/_register
{
  "name": "local_model_group",
  "description": "A model group for local models"
}

POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
  "version": "1.0.1",
  "model_group_id": "Z1eQf4oB5Vm0Tdw8EIP2",
  "model_format": "TORCH_SCRIPT"
}

GET /_plugins/_ml/tasks/czvQu40BP_SZARBdfA3D


POST /_plugins/_ml/models/hDvRu40BP_SZARBdjA2M/_deploy

```

Creating OpenSearch ingestion pipeline
```
PUT /_ingest/pipeline/nlp-fem-ingest-pipeline
{
  "description": "A text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "hDvRu40BP_SZARBdjA2M",
        "field_map": {
          "title": "title_embedding",
          "description": "description_embedding"
        }
      }
    }
  ]
}
```

Creating index
```
PUT /fem-search-nlp
{
  "mappings": {
    "properties": {
      "apply": {
        "properties": {
          "email": {
            "type": "keyword"
          }
        }
      },
      "suggestedOccupationalCategories": {
        "type": "nested"
      },
      "applyVia": {
        "type": "keyword"
      },
      "directApply": {
        "type": "boolean"
      },
      "isSponsored": {
        "type": "boolean"
      },
      "sponsoring": {
        "properties": {
          "campaignId": {
            "type": "keyword"
          },
          "creditType": {
            "type": "keyword"
          },
          "startedAt": {
            "type": "date"
          }
        }
      },
      "sponsoringCampaignId": {
        "type": "keyword"
      },
      "sponsoringStartedAt": {
        "type": "date"
      },
      "status": {
        "type": "keyword"
      },
      "id": {
        "type": "keyword"
      },
      "externalId": {
        "type": "keyword"
      },
      "created": {
        "type": "date"
      },
      "updated": {
        "type": "date"
      },
      "published": {
        "type": "date"
      },
      "posted": {
        "type": "date"
      },
      "expiration": {
        "type": "date"
      },
      "source": {
        "type": "keyword"
      },
      "scraped": {
        "type": "boolean"
      },
      "anonymous": {
        "type": "boolean"
      },
      "title": {
        "type": "text"
      },
      "title_embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
          "engine": "lucene",
          "space_type": "l2",
          "name": "hnsw",
          "parameters": {}
        }
      },
      "contract": {
        "properties": {
          "duration": {
            "properties": {
              "label": {
                "type": "text"
              },
              "durationInMonths": {
                "type": "integer"
              }
            }
          },
          "type": {
            "properties": {
              "id": {
                "type": "keyword"
              },
              "label": {
                "type": "text"
              }
            }
          }
        }
      },
      "location": {
        "properties": {
          "4_search": {
            "analyzer": "phrase_suggestor",
            "type": "text"
          },
          "departmentsPerimeters": {
            "properties": {
              "isoCode": {
                "type": "keyword"
              },
              "label": {
                "copy_to": [
                  "location.4_search"
                ],
                "type": "text"
              },
              "departmentPerimeter": {
                "type": "geo_shape",
                "strategy": "recursive"
              }
            }
          },
          "departmentIsoCodes": {
            "type": "keyword"
          },
          "provinceIsoCodes": {
            "type": "keyword"
          },
          "address": {
            "properties": {
              "label": {
                "copy_to": [
                  "location.4_search"
                ],
                "type": "text"
              },
              "number": {
                "type": "integer"
              },
              "street": {
                "type": "text"
              },
              "city": {
                "copy_to": [
                  "location.4_search"
                ],
                "type": "text",
                "fields": {
                  "keyword": {
                    "type": "keyword"
                  }
                }
              },
              "citySlug": {
                "type": "keyword"
              },
              "postalCode": {
                "type": "keyword"
              },
              "geoLoc": {
                "type": "geo_point"
              },
              "country": {
                "type": "keyword"
              },
              "hidden": {
                "type": "boolean"
              },
              "department": {
                "properties": {
                  "isoCode": {
                    "type": "keyword"
                  },
                  "label": {
                    "copy_to": [
                      "location.4_search"
                    ],
                    "type": "text",
                    "fields":{
                      "keyword":{
                        "type": "keyword"
                      }
                    }
                  },
                  "labelSlug": {
                    "type": "keyword"
                  }
                }
              },
              "province": {
                "properties": {
                  "isoCode": {
                    "type": "keyword"
                  },
                  "label": {
                    "copy_to": [
                      "location.4_search"
                    ],
                    "type": "text"
                  },
                  "labelSlug": {
                    "type": "keyword"
                  }
                }
              }
            }
          }
        }
      },
      "industries": {
        "properties": {
          "id": {
            "type": "keyword"
          },
          "label": {
            "type": "text",
            "fields": {
              "keyword": {
                "type":  "keyword"
              }
            }
          },
          "labelSlug": {
            "type":  "keyword"
          }
        }
      },
      "hiringOrganization": {
        "properties": {
          "overallRating": {
            "properties": {
              "count": {
                "type": "integer"
              },
              "value": {
                "type": "integer"
              }
            }
          },
          "id": {
            "type": "keyword"
          },
          "externalId": {
            "type": "keyword"
          },
          "legalName": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword"
              }
            }
          },
          "legalNameSlug":{
            "type":"keyword"
          },
          "description": {
            "type": "text"
          },
          "apeCode": {
            "type": "keyword"
          },
          "type": {
            "type": "keyword"
          },
          "slug": {
            "type": "keyword"
          },
          "siret": {
            "type": "keyword"
          },
          "siren": {
            "type": "keyword"
          },
          "logo80": {
            "type": "keyword"
          },
          "video": {
            "type": "keyword"
          }
        }
      },
      "position": {
        "properties": {
          "title": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword"
              }
            }
          },
          "titleSlug":{
            "type":"keyword"
          },
          "description": {
            "type": "text"
          },
          "description_embedding": {
            "type": "knn_vector",
            "dimension": 384,
            "method": {
              "engine": "lucene",
              "space_type": "l2",
              "name": "hnsw",
              "parameters": {}
            }
          },
          "profileStatus": {
            "type": "keyword"
          },
          "video": {
            "type": "keyword"
          },
          "skills": {
            "properties": {
              "id": {
                "type": "keyword"
              },
              "label": {
                "type": "text"
              }
            }
          },
          "experienceRequirements": {
            "properties": {
              "id": {
                "type": "keyword"
              },
              "label": {
                "type": "text"
              }
            }
          },
          "educationRequirements": {
            "properties": {
              "id": {
                "type": "keyword"
              },
              "label": {
                "type": "text"
              }
            }
          },
          "occupationalCategory": {
            "properties": {
              "id": {
                "type": "keyword"
              },
              "label": {
                "type": "text"
              }
            }
          }
        }
      },
      "compensation": {
        "properties": {
          "label": {
            "type": "keyword"
          },
          "annualSalary": {
            "properties": {
              "min": {
                "type": "integer"
              },
              "max": {
                "type": "integer"
              }
            }
          },
          "salary": {
            "properties": {
              "min": {
                "type": "integer"
              },
              "max": {
                "type": "integer"
              },
              "basePeriod": {
                "type": "keyword"
              },
              "currency": {
                "type": "keyword"
              }
            }
          }
        }
      },
      "mainOccupationalCategory": {
        "properties": {
          "id": {
            "type": "keyword"
          },
          "label": {
            "type": "text"
          }
        }
      },
      "secondaryOccupationalCategories": {
        "properties": {
          "id": {
            "type": "keyword"
          },
          "label": {
            "type": "text"
          }
        }
      }
    }
  },
  "settings": {
    "index.knn": true,
    "default_pipeline": "nlp-fem-ingest-pipeline",
    "index": {
      "analysis": {
        "analyzer": {
          "default": {
            "filter": [
              "lowercase",
              "elision",
              "word_delimiter",
              "asciifolding",
              "stop",
              "keyword_marker",
              "stemmer_light_french"
            ],
            "tokenizer": "whitespace",
            "type": "custom"
          },
          "default_search": {
            "filter": [
              "lowercase",
              "elision",
              "word_delimiter",
              "asciifolding",
              "stop",
              "keyword_marker",
              "stemmer_light_french"
            ],
            "tokenizer": "whitespace",
            "type": "custom"
          },
          "phrase_suggestor": {
            "char_filter": [
              "html_strip"
            ],
            "filter": [
              "lowercase",
              "filter_shingle",
              "asciifolding"
            ],
            "tokenizer": "whitespace",
            "type": "custom"
          }
        },
        "filter": {
          "asciifolding": {
            "type": "asciifolding"
          },
          "elision": {
            "articles": [
              "l",
              "m",
              "t",
              "qu",
              "n",
              "s",
              "j",
              "d",
              "c",
              "jusqu",
              "quoiqu",
              "lorsqu",
              "puisqu"
            ],
            "type": "elision"
          },
          "filter_shingle": {
            "max_shingle_size": "5",
            "min_shingle_size": "3",
            "output_unigrams": "true",
            "type": "shingle"
          },
          "keyword_marker": {
            "keywords": [
              "directeur",
              "directrice",
              "commerciale",
              "commercial"
            ],
            "type": "keyword_marker"
          },
          "stemmer_light_french": {
            "name": "light_french",
            "type": "stemmer"
          },
          "stop": {
            "ignore_case": "true",
            "stopwords": [
              "a",
              "alors",
              "and",
              "au",
              "aucun",
              "aussi",
              "autre",
              "avant",
              "avec",
              "avoir",
              "bon",
              "car",
              "ce",
              "cela",
              "certains",
              "ces",
              "cet",
              "cette",
              "ceux",
              "chaque",
              "ci",
              "comme",
              "comment",
              "dans",
              "de",
              "des",
              "du",
              "dedans",
              "dehors",
              "depuis",
              "deux",
              "devrait",
              "doit",
              "donc",
              "dos",
              "droite",
              "debut",
              "e",
              "elle",
              "elles",
              "en",
              "encore",
              "essai",
              "est",
              "et",
              "eu",
              "euse",
              "fait",
              "faites",
              "fois",
              "font",
              "force",
              "haut",
              "hors",
              "ici",
              "il",
              "ils",
              "je",
              "juste",
              "la",
              "le",
              "les",
              "leur",
              "la",
              "ma",
              "maintenant",
              "mais",
              "mes",
              "mine",
              "moins",
              "mon",
              "mot",
              "meme",
              "ni",
              "nommes",
              "notre",
              "nous",
              "nouveaux",
              "or",
              "ou",
              "par",
              "parce",
              "parole",
              "pas",
              "personnes",
              "peut",
              "peu",
              "piece",
              "plupart",
              "pour",
              "pourquoi",
              "quand",
              "que",
              "quel",
              "quelle",
              "quelles",
              "quelques",
              "quels",
              "qui",
              "sa",
              "sans",
              "ses",
              "seulement",
              "sien",
              "son",
              "sont",
              "sous",
              "soyez",
              "sujet",
              "sur",
              "ta",
              "tandis",
              "tellement",
              "tels",
              "tes",
              "ton",
              "tous",
              "tout",
              "trop",
              "tres",
              "trice",
              "tu",
              "valeur",
              "voie",
              "voient",
              "vont",
              "votre",
              "vous",
              "vu",
              "ca",
              "etaient",
              "etait",
              "etions",
              "ete",
              "etre"
            ],
            "type": "stop"
          },
          "word_delimiter": {
            "split_on_numerics": "false",
            "type": "word_delimiter",
            "type_table": [
              "#=>ALPHANUM",
              "@=>ALPHANUM",
              "&=>ALPHANUM",
              "+=>ALPHANUM"
            ]
          }
        }
      },
      "max_result_window": "30000",
      "refresh_interval": "-1",
      "number_of_shards": 2,
      "number_of_replicas": 0,
      "translog": {
        "durability": "async",
        "sync_interval": "60s"
      }
    }
  }
}

```

Setting up search pipeline
```
GET /_nodes/search_pipelines


PUT /_search/pipeline/default_model_pipeline
{
  "request_processors": [
    {
      "neural_query_enricher" : {
        "default_model_id": "hDvRu40BP_SZARBdjA2M"
      }
    }
  ]
}


PUT /fem-search-nlp/_settings
{
  "index.search.default_pipeline" : "default_model_pipeline"
}


GET /fem-search-nlp/_search
{
  "query": {
    "neural": {
      "title_embedding": {
        "query_text": "agent immobilier",
        "k": 5
      }
    }
  }
}

```
Setting up hybrid Search
```
PUT /_search/pipeline/nlp-hybrid-search-pipeline
{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [
              0.3,
              0.7
            ]
          }
        }
      }
    }
  ]
}



GET /fem-search-nlp/_search?search_pipeline=nlp-hybrid-search-pipeline
{
  "_source": {
    "exclude": [
      "title_embedding",
      "description_embedding"
    ]
  },
  "query": {
    "hybrid": {
      "queries": [
        {
          "match": {
            "text": {
              "query": "Agent Immobilier"
            }
          }
        },
        {
          "neural": {
            "title_embedding": {
              "query_text": "Agent Immobilier",
              "model_id": "hDvRu40BP_SZARBdjA2M",
              "k": 5
            }
          }
        }
      ]
    }
  }
}

```