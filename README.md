## Introduction

A toy interpreted language based on the H2 computing pseudocode guide.  
  
This was created due to the lack of existing interpreters that follow the H2 computing pseudocode standard, and as such, is meant as a tool to help students practice and better familiarise themselves with the syntax rules of pseudocode.  

---

## Features

- [x] comments  
- [x] i/o    
- [x] primitive types (`INTEGER`, `REAL`, `BOOLEAN`, `STRING`, `CHAR`)  
- [x] type casting  
- [x] operators (arithemtic, logical, comparative)
- [x] variables, constants  
- [x] scoping
- [x] flow control (`IF`, `CASE`, `FOR`, `WHILE`, `REPEAT UNTIL`)  
- [x] subroutines (`PROCEDURE`, `FUNCTION`)
- [x] 1D arrays
- [ ] 2D arrays

---

## Setup

### Full Windows support
```bash
git clone jeff-160/Pseudocode-Interpreter
cd Pseudocode-Interpreter
setup.bat

pseudo <filename>
```

### Run with Python
```bash
pip install lark

python main.py <filename>
```

--- 

## Documentation

Refer to the [pseudocode guide](documentation.pdf) for the specific syntax rules.  

--- 

## Notes

- Strict typing is enforced (ie. no implicit type casting)
- `CHAR` and `STRING` use different quotes: `''` and `""` respectively
- `STRING` and `ARRAY` are 1-indexed
- Arguments are passed into subroutines by value, not reference