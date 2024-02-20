# guardrails-demo

### Introduction

### Deployment

```bash
chainlit run app.py -w
```



### Configuration
The guardrails configuration for this demo is structured as follows: 

#TODO change later

```
.src/
├── config/
│   ├── __init__.py
│   ├── rails/
│   │   ├── factcheck.co
│   │   ├── general.co
│   │   └── inputcheck.co
│   ├── kb
│   │   └── report.md
│   └── config.yml
```

The following rails are implemented:
- Input Validation
- Ouput Validation
- General Guidance