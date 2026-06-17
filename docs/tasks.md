# InvoiceKit MVP — Tasks de Implementação

## Etapa 1: Fundação do Projeto ✅
1. Configurar projeto FastAPI com Python 3.11+, Poetry/uv e estrutura de pastas
2. Configurar Docker Compose com PostgreSQL e Redis
3. Configurar SQLAlchemy async + Alembic para migrations
4. Implementar modelo `users` com enum de planos (free/pro)
5. Configurar dependência de banco de dados (async session)
6. Configurar Pydantic settings para variáveis de ambiente

## Etapa 2: Autenticação (Users/Auth) ✅
7. Implementar registro de usuário com hash de senha (bcrypt/argon2)
8. Implementar login com geração de JWT access token + refresh token
9. Implementar endpoint de refresh token
10. Implementar extração do usuário atual via dependency injection (`current_user`)
11. Implementar endpoints GET/PUT `/users/me`

## Etapa 3: Multi-Tenancy e Isolamento
12. Implementar middleware/dependency para verificação de `tenant_id` em todos os endpoints
13. Garantir que queries filtram por `tenant_id` do usuário autenticado

## Etapa 4: CRUD de Clientes
14. Implementar modelo `clients` com soft delete
15. Implementar repositório de clients com paginação e filtros (nome, email)
16. Implementar service de clients com verificação de limite do plano (5 free)
17. Implementar endpoints: POST, GET (list/get), PUT, DELETE `/clients`
18. Retornar HTTP 402 quando limite do plano for excedido

## Etapa 5: CRUD de Invoices (Draft)
19. Implementar modelo `invoices` com enum de status e soft delete
20. Implementar modelo `invoice_items` com cascade delete
21. Implementar lógica de numeração sequencial por tenant com proteção contra race condition (SELECT FOR UPDATE)
22. Implementar service de invoices com verificação de limite mensal (10 free)
23. Implementar endpoints: POST, GET (list/get), PUT, DELETE `/invoices`
24. Implementar cálculo automático de total a partir dos line items

## Etapa 6: Máquina de Estados das Invoices
25. Implementar transição `draft → sent` via POST `/invoices/{id}/send`
26. Implementar transição `sent → paid` manual via POST `/invoices/{id}/pay`
27. Implementar validação de transições inválidas (HTTP 400)
28. Imutabilidade: impedir update/delete de invoices não-draft

## Etapa 7: Geração de PDF
29. Configurar WeasyPrint + Jinja2
30. Criar template HTML/CSS para PDF (A4, dados do business, cliente, itens, totais, pagamento)
31. Implementar endpoint GET `/invoices/{id}/pdf` com StreamingResponse (BytesIO, sem storage em disco)

## Etapa 8: Integração Stripe
32. Configurar cliente Stripe e variáveis de ambiente
33. Implementar criação de Stripe Payment Link em POST `/invoices/{id}/payment-link`
34. Implementar endpoint POST `/webhooks/stripe` com validação de assinatura
35. Processar evento `checkout.session.completed`: marcar invoice como paid + `paid_at`
36. Implementar idempotência no webhook (se invoice já está paid, retornar 200 sem efeito colateral)

## Etapa 9: Celery Tasks
37. Configurar Celery + Redis como broker
38. Implementar task de envio de email com PDF anexado (triggered ao marcar como sent)
39. Implementar task de verificação de overdue (Celery Beat, a cada 15 min): `sent` → `overdue`
40. Garantir idempotência nas tasks (email duplicado, transição duplicada)

## Etapa 10: Endpoints Complementares
41. Implementar endpoint GET `/plans/usage` (clientes ativos vs limite, invoices no mês vs limite)
42. Retornar erros claros e descritivos conforme contract do PRD

## Etapa 11: Testes
43. Configurar Pytest + httpx + Testcontainers (PostgreSQL)
44. Criar fixtures: factories para users, clients, invoices
45. Testes de fluxo de auth (register, login, refresh, current user)
46. Testes de CRUD de clients com verificação de limites
47. Testes de CRUD de invoices com transições de status
48. Testes de numeração sequencial (multi-tenant, sem gaps)
49. Testes de isolamento de tenant
50. Testes de PDF (HTTP 200, content-type PDF, bytes válidos)
51. Testes de webhook Stripe (evento mockado com assinatura válida)
52. Testes de Celery tasks (email e overdue)

## Etapa 12: Deploy e Infraestrutura
53. Configurar Dockerfile para a aplicação
54. Configurar variáveis de ambiente para produção
55. Configurar CI (lint, testes, build de imagem)
56. Configurar endpoints de health check
