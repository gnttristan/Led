# Instructions for code generation
- Fixing code issue / bug : ALWAYS try to search what the architectural issue is / the robust fix in correct subclass / implementation is instead of implementing a quick fix
- ALWAYS fix with minimal changes, no redundant if/else, x.get("a") or x.get("a"), keep it MINIMAL and DETERMINISTIC
- AVOID WHEN POSSIBLE setattr, getattr, isinstance, because if it is required, then the issue result on the class architectures, it SHOULD work on class.attribute without extra handling
- answers should be short, straight to the point, minimum token output usage for explanations 