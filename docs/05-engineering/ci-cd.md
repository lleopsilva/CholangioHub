# CI/CD

---

# Objetivo

Automatizar validação e entrega.

---

# Plataforma

GitHub Actions

---

# Pipeline

```mermaid
flowchart LR

A[Commit]

B[Lint]

C[Test]

D[Build Docker]

E[Security Scan]

F[Deploy]

A --> B
B --> C
C --> D
D --> E
E --> F
Pull Request

Obrigatório:

testes passando;
revisão;
documentação atualizada.