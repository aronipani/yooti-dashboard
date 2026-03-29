# Python Constitution — yooti-dashboard

## Purpose
Defines how Python is written across agents, batch jobs, and API services.
Agent reads this before writing any Python file.

---

## Naming conventions

Variables and functions:     snake_case
  user_count = 0             ✓
  userCount = 0              ✗

Classes:                     PascalCase
  class PaymentService:      ✓
  class payment_service:     ✗

Constants (module-level):    UPPER_SNAKE_CASE
  MAX_RETRY_COUNT = 3        ✓

Private methods:             _single_leading_underscore
  def _validate_input(self)  ✓

Files and directories:       snake_case
  payment_service.py         ✓
  PaymentService.py          ✗

Never abbreviate:
  user_count not usr_cnt
  response not resp (except in FastAPI handler signatures)
  configuration not cfg

---

## File structure — every Python file follows this order

1. Module docstring (what this module does)
2. Imports:
   a. Standard library (os, sys, datetime, typing)
   b. Third-party (fastapi, pydantic, langchain, boto3)
   c. Local application (from .models import User)
   Blank line between groups. Alphabetical within groups.
3. Module-level constants
4. Classes
5. Functions (if not in a class)
6. if __name__ == "__main__": — entry points only

---

## Type annotations — mandatory everywhere

Every function parameter must have a type annotation.
Every function must have a return type annotation.
Run mypy strict — 0 errors is a hard requirement.

  def get_user(user_id: str) -> User:                        ✓
  def get_user(user_id):                                     ✗

  async def process(request: PaymentRequest) -> PaymentResult:  ✓

Use Optional for nullable:
  def find_user(user_id: str) -> Optional[User]:             ✓
  def find_user(user_id: str) -> User | None:                ✓ (Python 3.10+)

Use Pydantic models for all external data:
  class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)

---

## Error handling

Never use bare except:
  except:                                                    ✗
  except Exception as e:                                     ✓
  except (ValueError, TypeError) as e:                       ✓ (preferred — specific)

Define custom exceptions for domain errors:
  class PaymentFailedError(AppError):
    def __init__(self, reason: str, user_id: str) -> None:
      super().__init__(f"Payment failed: {reason}")
      self.user_id = user_id

Always log before re-raising:
  except Exception as e:
    log.error("payment.failed", error=str(e), user_id=user_id)
    raise PaymentFailedError(str(e), user_id) from e

Never swallow exceptions:
  except Exception:
    pass                                                     ✗

---

## Logging — structlog mandatory

  import structlog
  log = structlog.get_logger()

Log at entry of every public function:
  log.info("payment.start", user_id=user_id, amount=amount)

Log at exit with result context:
  log.info("payment.complete", user_id=user_id, payment_id=result.id)

Log errors with full context:
  log.error("payment.failed", user_id=user_id, error=str(e))

Never log sensitive data:
  log.info("auth.login", password=password)                  ✗
  log.info("auth.login", user_id=user_id)                    ✓

---

## Testing — pytest mandatory

One test file per source file:
  payment_service.py → test_payment_service.py

Test class per function under test:
  class TestProcessPayment:
    def test_returns_payment_id_on_success(self): ...
    def test_raises_on_insufficient_funds(self): ...

Test method names — always descriptive:
  def test_returns_payment_id_on_success(self):              ✓
  def test_1(self):                                          ✗

Every test is independent — no shared mutable state between tests.

All AWS services must use moto:
  from moto import mock_aws
  @mock_aws
  def test_uploads_to_s3(self): ...

Never make real network calls in tests.
Never access real databases in unit tests — mock the repository layer.

---

## Async patterns

Use async/await for all I/O bound operations:
  async def fetch_user(user_id: str) -> User:
    return await db.users.find_one(user_id)

Never use synchronous I/O inside an async function:
  async def handler():
    data = requests.get(url)                                 ✗ blocking
    data = await httpx.get(url)                              ✓ async

Use asyncio.gather for concurrent operations:
  user, orders = await asyncio.gather(
    get_user(user_id),
    get_orders(user_id)
  )

---

## What is banned

Global mutable state outside of dependency injection
Wildcard imports: from module import *                       ✗
Mutable default arguments: def fn(items=[]):                 ✗
String formatting in SQL queries (use parameterised)
Any use of eval() or exec()
Synchronous HTTP calls in async contexts (use httpx or aiohttp)
print() in production code — use structlog
Hardcoded credentials anywhere — use environment variables
