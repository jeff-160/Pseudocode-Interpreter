## Introduction

A toy interpreted language based on the H2 computing pseudocode guide.  
  
This was created due to the lack of existing interpreters that follow the H2 computing pseudocode standard, and as such, is meant as a tool to help students practice and better familiarise themselves with the syntax rules of pseudocode.  

---

## Features

- [x] comments  
- [x] i/o    
- [x] primitive types (`INTEGER`, `REAL`, `BOOLEAN`, `STRING`)  
- [x] type casting  
- [x] variables, constants  
- [x] scoping
- [x] flow control (`IF`, `CASE`, `FOR`, `WHILE`, `REPEAT UNTIL`)  
- [x] subroutines (`PROCEDURE`, `FUNCTION`)
- [x] 1d-arrays
- [ ] 2d-arrays

---

## Requirements

```bash
pip install lark
```

--- 

## Documentation

Refer to the [pseudocode guide](???) for the specific syntax rules.  

--- 

## Notes

- The `CHAR` data type is not supported due to its similarity with the `STRING` data type
- As of now, passing an `ARRAY` into subroutines is currently not supported