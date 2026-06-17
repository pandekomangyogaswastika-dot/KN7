"""Backend API Testing for Kain Nusantara ERP/WMS System - Fase 1A Configuration Foundation"""
import requests
import sys
from datetime import datetime

class KainNusantaraAPITester:
    def __init__(self, base_url="https://po-refactor.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.order_ids = []
        self.product_ids = []
        self.wms_task_ids = []
        self.payment_term_ids = []
        self.approval_rule_ids = []
        self.entities = {}
        self.products = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, description=""):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        if description:
            print(f"   {description}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "endpoint": endpoint
                })

            try:
                return success, response.json() if response.text else {}
            except:
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e),
                "endpoint": endpoint
            })
            return False, {}

    def test_root(self):
        """Test root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "api/",
            200,
            description="Check if API is active"
        )
        return success

    def test_login(self, email, password, role):
        """Test login and get token"""
        success, response = self.run_test(
            f"Login as {role}",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password},
            description=f"Login with {email}"
        )
        if success and 'token' in response:
            self.tokens[role] = response['token']
            print(f"   Token stored for {role}")
            return True
        return False

    def test_dashboard(self, role):
        """Test dashboard endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping dashboard test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"Dashboard for {role}",
            "GET",
            "api/dashboard",
            200,
            token=token,
            description=f"Get dashboard metrics for {role}"
        )
        if success:
            print(f"   Metrics: {response.get('metrics', {})}")
        return success

    def test_products(self, role):
        """Test products endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping products test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"Products List for {role}",
            "GET",
            "api/products",
            200,
            token=token,
            description=f"Get products list for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                products = response
            else:
                products = response.get('products', [])
            print(f"   Found {len(products)} products")
        return success

    def test_customers(self, role):
        """Test customers endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping customers test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"Customers List for {role}",
            "GET",
            "api/customers",
            200,
            token=token,
            description=f"Get customers list for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                customers = response
            else:
                customers = response.get('customers', [])
            print(f"   Found {len(customers)} customers")
        return success

    def test_warehouses(self, role):
        """Test warehouses endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping warehouses test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"Warehouses List for {role}",
            "GET",
            "api/warehouses",
            200,
            token=token,
            description=f"Get warehouses list for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                warehouses = response
            else:
                warehouses = response.get('warehouses', [])
            print(f"   Found {len(warehouses)} warehouses")
        return success

    def test_sales_orders(self, role):
        """Test sales orders endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping sales orders test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"Sales Orders for {role}",
            "GET",
            "api/sales-orders",
            200,
            token=token,
            description=f"Get sales orders for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                orders = response
            else:
                orders = response.get('orders', [])
            print(f"   Found {len(orders)} orders")
        return success

    def test_uoms(self, role):
        """Test UOMs endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping UOMs test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"UOMs List for {role}",
            "GET",
            "api/uoms",
            200,
            token=token,
            description=f"Get UOMs list for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                uoms = response
            else:
                uoms = response.get('uoms', [])
            print(f"   Found {len(uoms)} UOMs")
        return success

    def test_users(self, role):
        """Test users endpoint (admin only)"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping users test for {role} - no token")
            return False
        
        # Only admin should be able to access users
        expected_status = 200 if role == "admin" else 403
        success, response = self.run_test(
            f"Users List for {role}",
            "GET",
            "api/users",
            expected_status,
            token=token,
            description=f"Get users list for {role} (admin only)"
        )
        if success and role == "admin":
            # Handle both list and dict responses
            if isinstance(response, list):
                users = response
            else:
                users = response.get('users', [])
            print(f"   Found {len(users)} users")
        return success

    def test_inventory(self, role):
        """Test inventory endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping inventory test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"Inventory Balances for {role}",
            "GET",
            "api/inventory/balances",
            200,
            token=token,
            description=f"Get inventory balances for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                balances = response
            else:
                balances = response.get('balances', [])
            print(f"   Found {len(balances)} inventory balances")
        return success

    def test_wms_tasks(self, role):
        """Test WMS tasks endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping WMS tasks test for {role} - no token")
            return False
        
        success, response = self.run_test(
            f"WMS Tasks for {role}",
            "GET",
            "api/wms/tasks",
            200,
            token=token,
            description=f"Get WMS tasks for {role}"
        )
        if success:
            # Handle both list and dict responses
            if isinstance(response, list):
                tasks = response
            else:
                tasks = response.get('tasks', [])
            print(f"   Found {len(tasks)} WMS tasks")
        return success

    def test_g2_sales_order_filtering(self, role):
        """Test G2 bug fix: Sales order filtering by status and customer_id"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping G2 test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing G2 Bug Fix: Sales Order Filtering for {role}")
        
        # Test 1: Get all orders (no filter)
        success, response = self.run_test(
            "G2: Get all sales orders",
            "GET",
            "api/sales-orders",
            200,
            token=token,
            description="Should return all 8 orders"
        )
        if success and isinstance(response, list):
            all_orders = response
            self.order_ids = [o.get('id') for o in all_orders if o.get('id')]
            print(f"   ✓ Found {len(all_orders)} total orders")
            if len(all_orders) != 8:
                print(f"   ⚠️  Expected 8 orders, got {len(all_orders)}")
        
        # Test 2: Filter by status=reserved
        success, response = self.run_test(
            "G2: Filter by status=reserved",
            "GET",
            "api/sales-orders?status=reserved",
            200,
            token=token,
            description="Should return ONLY reserved orders"
        )
        if success and isinstance(response, list):
            reserved_orders = response
            print(f"   ✓ Found {len(reserved_orders)} reserved orders")
            # Verify all returned orders have status=reserved
            non_reserved = [o for o in reserved_orders if o.get('status') != 'reserved']
            if non_reserved:
                print(f"   ❌ Found {len(non_reserved)} orders with wrong status!")
                for o in non_reserved:
                    print(f"      - {o.get('number')}: {o.get('status')}")
                return False
            else:
                print(f"   ✓ All returned orders have status=reserved")
        
        # Test 3: Filter by status=dispatched
        success, response = self.run_test(
            "G2: Filter by status=dispatched",
            "GET",
            "api/sales-orders?status=dispatched",
            200,
            token=token,
            description="Should return ONLY dispatched orders"
        )
        if success and isinstance(response, list):
            dispatched_orders = response
            print(f"   ✓ Found {len(dispatched_orders)} dispatched orders")
            # Verify all returned orders have status=dispatched
            non_dispatched = [o for o in dispatched_orders if o.get('status') != 'dispatched']
            if non_dispatched:
                print(f"   ❌ Found {len(non_dispatched)} orders with wrong status!")
                return False
            else:
                print(f"   ✓ All returned orders have status=dispatched")
        
        # Test 4: Filter by customer_id (use first order's customer_id)
        if all_orders and len(all_orders) > 0:
            customer_id = all_orders[0].get('customer_id')
            if customer_id:
                success, response = self.run_test(
                    "G2: Filter by customer_id",
                    "GET",
                    f"api/sales-orders?customer_id={customer_id}",
                    200,
                    token=token,
                    description=f"Should return orders for customer {customer_id}"
                )
                if success and isinstance(response, list):
                    customer_orders = response
                    print(f"   ✓ Found {len(customer_orders)} orders for customer {customer_id}")
                    # Verify all returned orders have the correct customer_id
                    wrong_customer = [o for o in customer_orders if o.get('customer_id') != customer_id]
                    if wrong_customer:
                        print(f"   ❌ Found {len(wrong_customer)} orders with wrong customer_id!")
                        return False
                    else:
                        print(f"   ✓ All returned orders have correct customer_id")
        
        return True
    
    def test_g9_dashboard_active_orders(self, role):
        """Test G9 bug fix: Dashboard active_orders metric calculation"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping G9 test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing G9 Bug Fix: Dashboard Active Orders Metric for {role}")
        
        # Get dashboard
        success, response = self.run_test(
            "G9: Dashboard metrics",
            "GET",
            "api/dashboard",
            200,
            token=token,
            description="Check active_orders metric calculation"
        )
        
        if success:
            metrics = response.get('metrics', {})
            active_orders = metrics.get('active_orders', 0)
            print(f"   ✓ Dashboard active_orders: {active_orders}")
            
            # Get all orders to verify
            success2, orders_response = self.run_test(
                "G9: Get all orders for verification",
                "GET",
                "api/sales-orders",
                200,
                token=token,
                description="Get all orders to verify active count"
            )
            
            if success2 and isinstance(orders_response, list):
                all_orders = orders_response
                # Count orders with status not in [done, cancelled, expired]
                actual_active = len([o for o in all_orders if o.get('status') not in ['done', 'cancelled', 'expired']])
                print(f"   ✓ Actual active orders (status not in [done,cancelled,expired]): {actual_active}")
                
                if active_orders == actual_active:
                    print(f"   ✅ G9 FIX VERIFIED: active_orders metric is correct!")
                    return True
                else:
                    print(f"   ❌ G9 FIX FAILED: active_orders={active_orders}, expected={actual_active}")
                    return False
        
        return False
    
    def test_g7_g6_document_preview(self, role):
        """Test G7/G6 bug fix: Document preview endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping G7/G6 test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing G7/G6 Bug Fix: Document Preview for {role}")
        
        # Test with specific order IDs: so_001, so_007, and one more
        test_order_ids = ['so_001', 'so_007', 'so_003']
        
        all_success = True
        for order_id in test_order_ids:
            success, response = self.run_test(
                f"G7/G6: Preview document for {order_id}",
                "GET",
                f"api/documents/preview/{order_id}",
                200,
                token=token,
                description=f"Should return HTML for order {order_id}"
            )
            if not success:
                all_success = False
                print(f"   ❌ Document preview failed for {order_id}")
            else:
                print(f"   ✅ Document preview successful for {order_id}")
        
        return all_success
    
    def test_g7_barcode_generation(self, role):
        """Test G7 bug fix: Barcode generation for products and WMS tasks"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping G7 barcode test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing G7 Bug Fix: Barcode Generation for {role}")
        
        # Get a product ID
        success, products_response = self.run_test(
            "G7: Get products for barcode test",
            "GET",
            "api/products",
            200,
            token=token,
            description="Get products to test barcode generation"
        )
        
        product_id = None
        if success:
            if isinstance(products_response, list) and len(products_response) > 0:
                product_id = products_response[0].get('id')
            elif isinstance(products_response, dict):
                products = products_response.get('products', [])
                if len(products) > 0:
                    product_id = products[0].get('id')
        
        # Test barcode generation for product
        if product_id:
            success, response = self.run_test(
                "G7: Generate barcode for product",
                "POST",
                "api/documents/barcode",
                200,
                data={"target_type": "product", "target_id": product_id, "label_size": "80x40"},
                token=token,
                description=f"Generate barcode for product {product_id}"
            )
            if success and response.get('label_html'):
                print(f"   ✅ Product barcode generated successfully")
            else:
                print(f"   ❌ Product barcode generation failed")
                return False
        
        # Get a WMS task ID
        success, tasks_response = self.run_test(
            "G7: Get WMS tasks for barcode test",
            "GET",
            "api/wms/tasks",
            200,
            token=token,
            description="Get WMS tasks to test barcode generation"
        )
        
        wms_task_id = None
        if success:
            if isinstance(tasks_response, list) and len(tasks_response) > 0:
                wms_task_id = tasks_response[0].get('id')
            elif isinstance(tasks_response, dict):
                tasks = tasks_response.get('tasks', [])
                if len(tasks) > 0:
                    wms_task_id = tasks[0].get('id')
        
        # Test barcode generation for WMS task
        if wms_task_id:
            success, response = self.run_test(
                "G7: Generate barcode for WMS task",
                "POST",
                "api/documents/barcode",
                200,
                data={"target_type": "wms_task", "target_id": wms_task_id, "label_size": "80x40"},
                token=token,
                description=f"Generate barcode for WMS task {wms_task_id}"
            )
            if success and response.get('label_html'):
                print(f"   ✅ WMS task barcode generated successfully")
                return True
            else:
                print(f"   ❌ WMS task barcode generation failed")
                return False
        
        return True
    
    def test_g1_sales_order_fields(self, role):
        """Test G1 bug fix: Sales orders must have quantity, sales_name, shipping_city"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping G1 test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing G1 Bug Fix: Sales Order Required Fields for {role}")
        
        # Get all orders
        success, response = self.run_test(
            "G1: Get all sales orders",
            "GET",
            "api/sales-orders",
            200,
            token=token,
            description="Check all orders have required fields"
        )
        
        if success and isinstance(response, list):
            orders = response
            print(f"   ✓ Checking {len(orders)} orders for required fields")
            
            missing_fields = []
            for order in orders:
                order_id = order.get('number', order.get('id'))
                issues = []
                
                # Check items have quantity
                items = order.get('items', [])
                for idx, item in enumerate(items):
                    if item.get('quantity') is None:
                        issues.append(f"item[{idx}].quantity is null")
                
                # Check order has sales_name
                if not order.get('sales_name'):
                    issues.append("sales_name is missing or null")
                
                # Check order has shipping_city
                if not order.get('shipping_city'):
                    issues.append("shipping_city is missing or null")
                
                if issues:
                    missing_fields.append({
                        'order': order_id,
                        'issues': issues
                    })
            
            if missing_fields:
                print(f"   ❌ G1 FIX FAILED: Found {len(missing_fields)} orders with missing fields:")
                for mf in missing_fields:
                    print(f"      - {mf['order']}: {', '.join(mf['issues'])}")
                return False
            else:
                print(f"   ✅ G1 FIX VERIFIED: All orders have required fields!")
                return True
        
        return False
    
    def test_order_lifecycle(self, role):
        """Test order lifecycle: approve and confirm flows"""
        token = self.tokens.get(role)
        if not token or role not in ['admin', 'manager']:
            print(f"⚠️  Skipping order lifecycle test for {role} - requires admin/manager")
            return False
        
        print(f"\n🔍 Testing Order Lifecycle: Approve & Confirm for {role}")
        
        # Get all orders to find a waiting_approval order
        success, response = self.run_test(
            "Lifecycle: Get orders",
            "GET",
            "api/sales-orders",
            200,
            token=token,
            description="Find a waiting_approval order"
        )
        
        if success and isinstance(response, list):
            orders = response
            waiting_approval_order = next((o for o in orders if o.get('status') == 'waiting_approval'), None)
            
            if waiting_approval_order:
                order_id = waiting_approval_order.get('id')
                print(f"   ✓ Found waiting_approval order: {waiting_approval_order.get('number')}")
                
                # Test approve
                success, response = self.run_test(
                    "Lifecycle: Approve order",
                    "POST",
                    f"api/sales-orders/{order_id}/approve",
                    200,
                    token=token,
                    description=f"Approve order {order_id}"
                )
                
                if success:
                    print(f"   ✅ Order approved successfully")
                    new_status = response.get('status')
                    print(f"   ✓ New status: {new_status}")
                    
                    # Test confirm on the approved order
                    if new_status in ['approved', 'reserved']:
                        success2, response2 = self.run_test(
                            "Lifecycle: Confirm order",
                            "POST",
                            f"api/sales-orders/{order_id}/confirm",
                            200,
                            token=token,
                            description=f"Confirm order {order_id}"
                        )
                        
                        if success2:
                            print(f"   ✅ Order confirmed successfully")
                            print(f"   ✓ Final status: {response2.get('status')}")
                            return True
                        else:
                            print(f"   ❌ Order confirmation failed")
                            return False
                else:
                    print(f"   ❌ Order approval failed")
                    return False
            else:
                print(f"   ⚠️  No waiting_approval order found, trying with reserved/approved order")
                # Try to find a reserved or approved order to confirm
                confirmable_order = next((o for o in orders if o.get('status') in ['reserved', 'approved']), None)
                if confirmable_order:
                    order_id = confirmable_order.get('id')
                    print(f"   ✓ Found {confirmable_order.get('status')} order: {confirmable_order.get('number')}")
                    
                    success, response = self.run_test(
                        "Lifecycle: Confirm order",
                        "POST",
                        f"api/sales-orders/{order_id}/confirm",
                        200,
                        token=token,
                        description=f"Confirm order {order_id}"
                    )
                    
                    if success:
                        print(f"   ✅ Order confirmed successfully")
                        return True
                    else:
                        print(f"   ❌ Order confirmation failed")
                        return False
        
        return False

    # ── FASE 1A: Configuration Foundation Tests ──────────────────────────────────
    
    def test_fase1a_get_settings(self, role):
        """Test GET /api/settings - return global settings"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping settings test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: GET /api/settings for {role}")
        success, response = self.run_test(
            "Fase1A: Get global settings",
            "GET",
            "api/settings",
            200,
            token=token,
            description="Should return global settings with tax, finance, sales, inventory"
        )
        
        if success:
            # Verify structure
            tax = response.get('tax', {})
            finance = response.get('finance', {})
            sales = response.get('sales', {})
            inventory = response.get('inventory', {})
            
            print(f"   ✓ Tax settings: ppn_rate={tax.get('ppn_rate')}, ppn_mode={tax.get('ppn_mode')}, efaktur_enabled={tax.get('efaktur_enabled')}")
            print(f"   ✓ Finance: base_currency={finance.get('base_currency')}, fiscal_year_end_month={finance.get('fiscal_year_end_month')}")
            print(f"   ✓ Sales: quotation_enabled={sales.get('quotation_enabled')}, allow_partial_shipment={sales.get('allow_partial_shipment')}")
            print(f"   ✓ Inventory: default_uom={inventory.get('default_uom')}, min_cut_qty={inventory.get('min_cut_qty')}")
            
            # Verify expected values
            if tax.get('ppn_rate') == 11 and tax.get('ppn_mode') == 'excluded' and tax.get('efaktur_enabled') == True:
                print(f"   ✅ Tax settings are correct (ppn_rate=11, ppn_mode=excluded, efaktur_enabled=true)")
            else:
                print(f"   ⚠️  Tax settings may not match expected defaults")
            
            if finance.get('base_currency') == 'IDR' and finance.get('fiscal_year_end_month') == 12:
                print(f"   ✅ Finance settings are correct")
            else:
                print(f"   ⚠️  Finance settings may not match expected defaults")
            
            return True
        return False
    
    def test_fase1a_get_effective_settings(self, role):
        """Test GET /api/settings/effective?entity_id - PKP logic"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping effective settings test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: GET /api/settings/effective for {role}")
        
        # Test 1: entity_id=ent_ksc (PKP true)
        success1, response1 = self.run_test(
            "Fase1A: Effective settings for ent_ksc (PKP)",
            "GET",
            "api/settings/effective?entity_id=ent_ksc",
            200,
            token=token,
            description="Should return settings with is_pkp=true, ppn_rate=11"
        )
        
        if success1:
            tax1 = response1.get('tax', {})
            is_pkp1 = tax1.get('is_pkp')
            ppn_rate1 = tax1.get('ppn_rate')
            print(f"   ✓ ent_ksc: is_pkp={is_pkp1}, ppn_rate={ppn_rate1}")
            
            if is_pkp1 == True and ppn_rate1 == 11:
                print(f"   ✅ ent_ksc PKP settings are correct")
            else:
                print(f"   ❌ ent_ksc PKP settings incorrect: expected is_pkp=True, ppn_rate=11")
                return False
        
        # Test 2: entity_id=ent_kanda (non-PKP)
        success2, response2 = self.run_test(
            "Fase1A: Effective settings for ent_kanda (non-PKP)",
            "GET",
            "api/settings/effective?entity_id=ent_kanda",
            200,
            token=token,
            description="Should return settings with is_pkp=false, ppn_rate=0"
        )
        
        if success2:
            tax2 = response2.get('tax', {})
            is_pkp2 = tax2.get('is_pkp')
            ppn_rate2 = tax2.get('ppn_rate')
            print(f"   ✓ ent_kanda: is_pkp={is_pkp2}, ppn_rate={ppn_rate2}")
            
            if is_pkp2 == False and ppn_rate2 == 0:
                print(f"   ✅ ent_kanda non-PKP settings are correct")
            else:
                print(f"   ❌ ent_kanda non-PKP settings incorrect: expected is_pkp=False, ppn_rate=0")
                return False
        
        return success1 and success2
    
    def test_fase1a_update_settings(self, role):
        """Test PUT /api/settings - update global settings"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping update settings test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: PUT /api/settings for {role}")
        
        # Test: Update ppn_rate to 12
        success1, response1 = self.run_test(
            "Fase1A: Update ppn_rate to 12",
            "PUT",
            "api/settings",
            200,
            data={
                "scope": "global",
                "tax": {
                    "ppn_rate": 12,
                    "ppn_mode": "excluded",
                    "efaktur_enabled": True
                }
            },
            token=token,
            description="Should update ppn_rate to 12"
        )
        
        if success1:
            print(f"   ✅ Settings updated successfully")
            
            # Verify the update by getting settings again
            success2, response2 = self.run_test(
                "Fase1A: Verify ppn_rate=12",
                "GET",
                "api/settings",
                200,
                token=token,
                description="Should return ppn_rate=12"
            )
            
            if success2:
                tax = response2.get('tax', {})
                ppn_rate = tax.get('ppn_rate')
                print(f"   ✓ Verified ppn_rate={ppn_rate}")
                
                if ppn_rate == 12:
                    print(f"   ✅ ppn_rate update verified")
                    
                    # Restore to 11
                    success3, _ = self.run_test(
                        "Fase1A: Restore ppn_rate to 11",
                        "PUT",
                        "api/settings",
                        200,
                        data={
                            "scope": "global",
                            "tax": {
                                "ppn_rate": 11,
                                "ppn_mode": "excluded",
                                "efaktur_enabled": True
                            }
                        },
                        token=token,
                        description="Restore ppn_rate to 11"
                    )
                    if success3:
                        print(f"   ✓ Restored ppn_rate to 11")
                    return True
                else:
                    print(f"   ❌ ppn_rate not updated correctly: expected 12, got {ppn_rate}")
                    return False
        
        return False
    
    def test_fase1a_compute_tax(self, role):
        """Test GET /api/settings/compute-tax - tax calculation"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping compute tax test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: GET /api/settings/compute-tax for {role}")
        
        # Test 1: ent_ksc (PKP) - subtotal 1000000
        success1, response1 = self.run_test(
            "Fase1A: Compute tax for ent_ksc (PKP)",
            "GET",
            "api/settings/compute-tax?subtotal=1000000&entity_id=ent_ksc",
            200,
            token=token,
            description="Should return ppn_amount=110000, grand_total=1110000"
        )
        
        if success1:
            ppn_amount1 = response1.get('ppn_amount')
            grand_total1 = response1.get('grand_total')
            print(f"   ✓ ent_ksc: ppn_amount={ppn_amount1}, grand_total={grand_total1}")
            
            if ppn_amount1 == 110000 and grand_total1 == 1110000:
                print(f"   ✅ ent_ksc tax calculation correct")
            else:
                print(f"   ❌ ent_ksc tax calculation incorrect: expected ppn_amount=110000, grand_total=1110000")
                return False
        
        # Test 2: ent_kanda (non-PKP) - subtotal 1000000
        success2, response2 = self.run_test(
            "Fase1A: Compute tax for ent_kanda (non-PKP)",
            "GET",
            "api/settings/compute-tax?subtotal=1000000&entity_id=ent_kanda",
            200,
            token=token,
            description="Should return ppn_amount=0, grand_total=1000000"
        )
        
        if success2:
            ppn_amount2 = response2.get('ppn_amount')
            grand_total2 = response2.get('grand_total')
            print(f"   ✓ ent_kanda: ppn_amount={ppn_amount2}, grand_total={grand_total2}")
            
            if ppn_amount2 == 0 and grand_total2 == 1000000:
                print(f"   ✅ ent_kanda tax calculation correct (no PPN)")
            else:
                print(f"   ❌ ent_kanda tax calculation incorrect: expected ppn_amount=0, grand_total=1000000")
                return False
        
        return success1 and success2
    
    def test_fase1a_evaluate_approval(self, role):
        """Test GET /api/settings/evaluate-approval - approval rules evaluation"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping evaluate approval test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: GET /api/settings/evaluate-approval for {role}")
        
        # Test 1: sales_order, amount=250000000 (>200M) → requires admin
        success1, response1 = self.run_test(
            "Fase1A: Evaluate approval for 250M (admin required)",
            "GET",
            "api/settings/evaluate-approval?doc_type=sales_order&amount=250000000&entity_id=ent_ksc",
            200,
            token=token,
            description="Should return requires_approval=true, required_role=admin"
        )
        
        if success1:
            requires_approval1 = response1.get('requires_approval')
            required_role1 = response1.get('required_role')
            print(f"   ✓ 250M: requires_approval={requires_approval1}, required_role={required_role1}")
            
            if requires_approval1 == True and required_role1 == 'admin':
                print(f"   ✅ 250M approval rule correct (admin required)")
            else:
                print(f"   ❌ 250M approval rule incorrect: expected requires_approval=True, required_role=admin")
                return False
        
        # Test 2: sales_order, amount=10000000 (10M, <50M) → no approval
        success2, response2 = self.run_test(
            "Fase1A: Evaluate approval for 10M (no approval)",
            "GET",
            "api/settings/evaluate-approval?doc_type=sales_order&amount=10000000&entity_id=ent_ksc",
            200,
            token=token,
            description="Should return requires_approval=false"
        )
        
        if success2:
            requires_approval2 = response2.get('requires_approval')
            print(f"   ✓ 10M: requires_approval={requires_approval2}")
            
            if requires_approval2 == False:
                print(f"   ✅ 10M approval rule correct (no approval)")
            else:
                print(f"   ❌ 10M approval rule incorrect: expected requires_approval=False")
                return False
        
        # Test 3: sales_order, amount=100000000 (100M, 50M-200M) → requires manager
        success3, response3 = self.run_test(
            "Fase1A: Evaluate approval for 100M (manager required)",
            "GET",
            "api/settings/evaluate-approval?doc_type=sales_order&amount=100000000&entity_id=ent_ksc",
            200,
            token=token,
            description="Should return requires_approval=true, required_role=manager"
        )
        
        if success3:
            requires_approval3 = response3.get('requires_approval')
            required_role3 = response3.get('required_role')
            print(f"   ✓ 100M: requires_approval={requires_approval3}, required_role={required_role3}")
            
            if requires_approval3 == True and required_role3 == 'manager':
                print(f"   ✅ 100M approval rule correct (manager required)")
            else:
                print(f"   ❌ 100M approval rule incorrect: expected requires_approval=True, required_role=manager")
                return False
        
        return success1 and success2 and success3
    
    def test_fase1a_payment_terms_crud(self, role):
        """Test payment terms CRUD operations"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping payment terms test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: Payment Terms CRUD for {role}")
        
        # Test 1: GET /api/payment-terms - should return 6 default terms
        success1, response1 = self.run_test(
            "Fase1A: Get payment terms",
            "GET",
            "api/payment-terms",
            200,
            token=token,
            description="Should return 6 default terms (CASH, NET7, NET14, NET30, DP50, INST3)"
        )
        
        if success1:
            terms = response1 if isinstance(response1, list) else []
            print(f"   ✓ Found {len(terms)} payment terms")
            
            # Check for expected default terms
            codes = [t.get('code') for t in terms]
            expected_codes = ['CASH', 'NET7', 'NET14', 'NET30', 'DP50', 'INST3']
            missing_codes = [c for c in expected_codes if c not in codes]
            
            if len(missing_codes) == 0:
                print(f"   ✅ All 6 default payment terms found")
            else:
                print(f"   ⚠️  Missing default terms: {missing_codes}")
        
        # Test 2: POST /api/payment-terms - create new term
        unique_code = f"TEST{datetime.now().strftime('%H%M%S')}"
        success2, response2 = self.run_test(
            "Fase1A: Create payment term",
            "POST",
            "api/payment-terms",
            200,
            data={
                "code": unique_code,
                "name": "Test Term",
                "type": "credit",
                "net_days": 45,
                "dp_percent": 0,
                "installment_count": 0,
                "sort": 99,
                "active": True
            },
            token=token,
            description=f"Create new term with code {unique_code}"
        )
        
        term_id = None
        if success2:
            term_id = response2.get('id')
            print(f"   ✅ Payment term created: {term_id}")
        
        # Test 3: POST duplicate code - should return 409
        success3, response3 = self.run_test(
            "Fase1A: Create duplicate payment term (409)",
            "POST",
            "api/payment-terms",
            409,
            data={
                "code": unique_code,
                "name": "Duplicate Term",
                "type": "credit",
                "net_days": 60,
                "dp_percent": 0,
                "installment_count": 0,
                "sort": 99,
                "active": True
            },
            token=token,
            description=f"Should return 409 for duplicate code {unique_code}"
        )
        
        if success3:
            print(f"   ✅ Duplicate code correctly rejected with 409")
        
        # Test 4: PATCH /api/payment-terms/{id} - update term
        if term_id:
            success4, response4 = self.run_test(
                "Fase1A: Update payment term (active=false)",
                "PATCH",
                f"api/payment-terms/{term_id}",
                200,
                data={"data": {"active": False}},
                token=token,
                description=f"Set active=false for term {term_id}"
            )
            
            if success4:
                active = response4.get('active')
                print(f"   ✅ Payment term updated: active={active}")
                
                if active == False:
                    print(f"   ✅ Active status correctly set to False")
                else:
                    print(f"   ❌ Active status not updated correctly")
                    return False
        
        # Test 5: DELETE /api/payment-terms/{id} - soft delete
        if term_id:
            success5, response5 = self.run_test(
                "Fase1A: Delete payment term (soft delete)",
                "DELETE",
                f"api/payment-terms/{term_id}",
                200,
                token=token,
                description=f"Soft delete term {term_id}"
            )
            
            if success5:
                active = response5.get('active')
                print(f"   ✅ Payment term deleted (soft): active={active}")
                
                if active == False:
                    print(f"   ✅ Soft delete successful (active=False)")
                else:
                    print(f"   ❌ Soft delete failed: active should be False")
                    return False
        
        return success1 and success2 and success3 and (success4 if term_id else True) and (success5 if term_id else True)
    
    def test_fase1a_approval_rules_crud(self, role):
        """Test approval rules CRUD operations"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping approval rules test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Fase 1A: Approval Rules CRUD for {role}")
        
        # Test 1: GET /api/approval-rules - should return 7 default rules
        success1, response1 = self.run_test(
            "Fase1A: Get approval rules",
            "GET",
            "api/approval-rules",
            200,
            token=token,
            description="Should return 7 default rules"
        )
        
        if success1:
            rules = response1 if isinstance(response1, list) else []
            print(f"   ✓ Found {len(rules)} approval rules")
            
            # Count rules by doc_type
            sales_order_rules = [r for r in rules if r.get('doc_type') == 'sales_order']
            discount_rules = [r for r in rules if r.get('doc_type') == 'discount']
            purchase_order_rules = [r for r in rules if r.get('doc_type') == 'purchase_order']
            
            print(f"   ✓ Sales Order rules: {len(sales_order_rules)}")
            print(f"   ✓ Discount rules: {len(discount_rules)}")
            print(f"   ✓ Purchase Order rules: {len(purchase_order_rules)}")
            
            if len(sales_order_rules) >= 3 and len(discount_rules) >= 2 and len(purchase_order_rules) >= 2:
                print(f"   ✅ Default approval rules structure looks correct")
            else:
                print(f"   ⚠️  Default approval rules may be incomplete")
        
        # Test 2: POST /api/approval-rules - create new rule
        success2, response2 = self.run_test(
            "Fase1A: Create approval rule",
            "POST",
            "api/approval-rules",
            200,
            data={
                "doc_type": "transfer",
                "entity_id": "all",
                "min_amount": 0,
                "max_amount": 50000000,
                "required_role": "manager",
                "is_percent": False,
                "sort": 99,
                "active": True
            },
            token=token,
            description="Create new transfer approval rule"
        )
        
        rule_id = None
        if success2:
            rule_id = response2.get('id')
            print(f"   ✅ Approval rule created: {rule_id}")
        
        # Test 3: PATCH /api/approval-rules/{id} - update rule
        if rule_id:
            success3, response3 = self.run_test(
                "Fase1A: Update approval rule",
                "PATCH",
                f"api/approval-rules/{rule_id}",
                200,
                data={"data": {"required_role": "admin"}},
                token=token,
                description=f"Update required_role to admin for rule {rule_id}"
            )
            
            if success3:
                required_role = response3.get('required_role')
                print(f"   ✅ Approval rule updated: required_role={required_role}")
                
                if required_role == 'admin':
                    print(f"   ✅ Required role correctly updated to admin")
                else:
                    print(f"   ❌ Required role not updated correctly")
                    return False
        
        # Test 4: DELETE /api/approval-rules/{id} - hard delete
        if rule_id:
            success4, response4 = self.run_test(
                "Fase1A: Delete approval rule",
                "DELETE",
                f"api/approval-rules/{rule_id}",
                200,
                token=token,
                description=f"Delete rule {rule_id}"
            )
            
            if success4:
                print(f"   ✅ Approval rule deleted")
                
                # Verify deletion by trying to get the rule again
                success5, response5 = self.run_test(
                    "Fase1A: Verify rule deletion",
                    "GET",
                    "api/approval-rules",
                    200,
                    token=token,
                    description="Verify rule is deleted"
                )
                
                if success5:
                    rules = response5 if isinstance(response5, list) else []
                    deleted_rule = next((r for r in rules if r.get('id') == rule_id), None)
                    
                    if deleted_rule is None:
                        print(f"   ✅ Rule deletion verified (rule not found in list)")
                    else:
                        print(f"   ❌ Rule still exists after deletion")
                        return False
        
        return success1 and success2 and (success3 if rule_id else True) and (success4 if rule_id else True)

    # ── SUB-FASE 1.4: ATP & Fulfillment Modes Tests ──────────────────────────────
    
    def load_entities_and_products(self, role):
        """Load entities and products for ATP tests"""
        token = self.tokens.get(role)
        if not token:
            return False
        
        # Get entities
        success1, response1 = self.run_test(
            "Load entities",
            "GET",
            "api/entities",
            200,
            token=token,
            description="Load business entities"
        )
        if success1 and isinstance(response1, list):
            self.entities = {e.get('short_name'): e.get('id') for e in response1}
            print(f"   ✓ Loaded entities: {list(self.entities.keys())}")
        
        # Get products
        success2, response2 = self.run_test(
            "Load products",
            "GET",
            "api/products",
            200,
            token=token,
            description="Load products"
        )
        if success2:
            self.products = response2 if isinstance(response2, list) else []
            print(f"   ✓ Loaded {len(self.products)} products")
        
        return success1 and success2
    
    def find_product_id(self, name_fragment):
        """Find product ID by name fragment"""
        for p in self.products:
            if name_fragment.lower() in p.get('name', '').lower():
                return p.get('id')
        return None
    
    def test_subfase14_preview_allocation_from_stock(self, role):
        """Test preview-allocation: from_stock scenario"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping preview-allocation from_stock test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Sub-fase 1.4: Preview Allocation - from_stock for {role}")
        
        ksc_id = self.entities.get('KSC')
        batik_id = self.find_product_id('Batik Mega')
        
        if not ksc_id or not batik_id:
            print(f"   ⚠️  Missing entity or product: KSC={ksc_id}, Batik={batik_id}")
            return False
        
        success, response = self.run_test(
            "Sub-fase 1.4: from_stock (KSC, Batik 100m)",
            "POST",
            "api/sales-orders/preview-allocation",
            200,
            data={
                "entity_id": ksc_id,
                "items": [{"product_id": batik_id, "quantity": 100, "unit": "meter"}]
            },
            token=token,
            description="KSC sells Batik 100m → should be from_stock (avail 755)"
        )
        
        if success:
            lines = response.get('lines', [])
            if len(lines) > 0:
                line = lines[0]
                mode = line.get('primary_mode')
                own_available = line.get('own_available', 0)
                own_atp = line.get('own_atp', 0)
                breakdown = line.get('breakdown', {})
                
                print(f"   ✓ Mode: {mode}, Available: {own_available}, ATP: {own_atp}")
                print(f"   ✓ Breakdown: {breakdown}")
                
                if mode == 'from_stock' and own_available >= 100:
                    print(f"   ✅ from_stock scenario PASSED")
                    return True
                else:
                    print(f"   ❌ Expected mode=from_stock with available>=100, got mode={mode}, available={own_available}")
                    return False
        
        return False
    
    def test_subfase14_preview_allocation_from_incoming(self, role):
        """Test preview-allocation: from_incoming scenario"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping preview-allocation from_incoming test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Sub-fase 1.4: Preview Allocation - from_incoming for {role}")
        
        ksc_id = self.entities.get('KSC')
        ulos_id = self.find_product_id('Ulos')
        
        if not ksc_id or not ulos_id:
            print(f"   ⚠️  Missing entity or product: KSC={ksc_id}, Ulos={ulos_id}")
            return False
        
        success, response = self.run_test(
            "Sub-fase 1.4: from_incoming (KSC, Ulos 300m)",
            "POST",
            "api/sales-orders/preview-allocation",
            200,
            data={
                "entity_id": ksc_id,
                "items": [{"product_id": ulos_id, "quantity": 300, "unit": "meter"}]
            },
            token=token,
            description="KSC sells Ulos 300m → should be from_incoming (avail 235 + incoming 100 = ATP 335)"
        )
        
        if success:
            lines = response.get('lines', [])
            if len(lines) > 0:
                line = lines[0]
                mode = line.get('primary_mode')
                own_available = line.get('own_available', 0)
                own_incoming = line.get('own_incoming', 0)
                own_atp = line.get('own_atp', 0)
                breakdown = line.get('breakdown', {})
                
                print(f"   ✓ Mode: {mode}, Available: {own_available}, Incoming: {own_incoming}, ATP: {own_atp}")
                print(f"   ✓ Breakdown: {breakdown}")
                
                # ATP should be available + incoming
                expected_atp = own_available + own_incoming
                atp_match = abs(own_atp - expected_atp) < 0.1
                
                if mode == 'from_incoming' and own_atp >= 300 and atp_match:
                    print(f"   ✅ from_incoming scenario PASSED (ATP = available + incoming)")
                    return True
                else:
                    print(f"   ❌ Expected mode=from_incoming with ATP>=300, got mode={mode}, ATP={own_atp}")
                    return False
        
        return False
    
    def test_subfase14_preview_allocation_backorder(self, role):
        """Test preview-allocation: backorder scenario"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping preview-allocation backorder test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Sub-fase 1.4: Preview Allocation - backorder for {role}")
        
        ksc_id = self.entities.get('KSC')
        ulos_id = self.find_product_id('Ulos')
        
        if not ksc_id or not ulos_id:
            print(f"   ⚠️  Missing entity or product: KSC={ksc_id}, Ulos={ulos_id}")
            return False
        
        success, response = self.run_test(
            "Sub-fase 1.4: backorder (KSC, Ulos 400m)",
            "POST",
            "api/sales-orders/preview-allocation",
            200,
            data={
                "entity_id": ksc_id,
                "items": [{"product_id": ulos_id, "quantity": 400, "unit": "meter"}]
            },
            token=token,
            description="KSC sells Ulos 400m → should be backorder (ATP 335 < 400, backorder 65)"
        )
        
        if success:
            lines = response.get('lines', [])
            if len(lines) > 0:
                line = lines[0]
                mode = line.get('primary_mode')
                own_atp = line.get('own_atp', 0)
                breakdown = line.get('breakdown', {})
                backorder_qty = breakdown.get('backorder', 0)
                
                print(f"   ✓ Mode: {mode}, ATP: {own_atp}, Backorder: {backorder_qty}")
                print(f"   ✓ Breakdown: {breakdown}")
                
                if mode == 'backorder' and backorder_qty > 0:
                    print(f"   ✅ backorder scenario PASSED (backorder={backorder_qty})")
                    return True
                else:
                    print(f"   ❌ Expected mode=backorder with backorder>0, got mode={mode}, backorder={backorder_qty}")
                    return False
        
        return False
    
    def test_subfase14_preview_allocation_inter_company(self, role):
        """Test preview-allocation: inter_company scenario"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping preview-allocation inter_company test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Sub-fase 1.4: Preview Allocation - inter_company for {role}")
        
        kanda_id = self.entities.get('Kanda')
        batik_id = self.find_product_id('Batik Mega')
        
        if not kanda_id or not batik_id:
            print(f"   ⚠️  Missing entity or product: Kanda={kanda_id}, Batik={batik_id}")
            return False
        
        success, response = self.run_test(
            "Sub-fase 1.4: inter_company (Kanda, Batik 100m)",
            "POST",
            "api/sales-orders/preview-allocation",
            200,
            data={
                "entity_id": kanda_id,
                "items": [{"product_id": batik_id, "quantity": 100, "unit": "meter"}]
            },
            token=token,
            description="Kanda sells Batik 100m → should be inter_company (Kanda avail 0, KSC avail 755)"
        )
        
        if success:
            lines = response.get('lines', [])
            if len(lines) > 0:
                line = lines[0]
                mode = line.get('primary_mode')
                own_available = line.get('own_available', 0)
                other_entity_available = line.get('other_entity_available', 0)
                cross_entity = line.get('cross_entity', [])
                breakdown = line.get('breakdown', {})
                
                print(f"   ✓ Mode: {mode}, Own Available: {own_available}, Other Entity Available: {other_entity_available}")
                print(f"   ✓ Cross Entity: {[e.get('entity_name') for e in cross_entity]}")
                print(f"   ✓ Breakdown: {breakdown}")
                
                if mode == 'inter_company' and other_entity_available > 0 and len(cross_entity) > 0:
                    print(f"   ✅ inter_company scenario PASSED")
                    return True
                else:
                    print(f"   ❌ Expected mode=inter_company with other_entity_available>0, got mode={mode}, other={other_entity_available}")
                    return False
        
        return False
    
    def test_subfase14_inventory_status_board(self, role):
        """Test inventory status board endpoint"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping inventory status board test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Sub-fase 1.4: Inventory Status Board for {role}")
        
        success, response = self.run_test(
            "Sub-fase 1.4: Inventory Status Board",
            "GET",
            "api/inventory/status-board",
            200,
            token=token,
            description="Get inventory status board with ATP"
        )
        
        if success and isinstance(response, list):
            rows = response
            print(f"   ✓ Found {len(rows)} products in status board")
            
            if len(rows) == 0:
                print(f"   ❌ Status board is empty")
                return False
            
            # Check ATP consistency: total_atp == total_available + total_incoming
            atp_mismatches = []
            inter_company_count = 0
            
            for row in rows:
                product_name = row.get('product_name', 'Unknown')
                total_available = row.get('total_available', 0)
                total_incoming = row.get('total_incoming', 0)
                total_atp = row.get('total_atp', 0)
                has_intercompany = row.get('has_intercompany_opportunity', False)
                
                expected_atp = total_available + total_incoming
                if abs(total_atp - expected_atp) > 0.05:
                    atp_mismatches.append({
                        'product': product_name,
                        'expected': expected_atp,
                        'actual': total_atp
                    })
                
                if has_intercompany:
                    inter_company_count += 1
            
            print(f"   ✓ Products with inter-company opportunity: {inter_company_count}")
            
            if atp_mismatches:
                print(f"   ❌ ATP calculation mismatches found:")
                for m in atp_mismatches[:3]:  # Show first 3
                    print(f"      - {m['product']}: expected ATP={m['expected']}, got {m['actual']}")
                return False
            else:
                print(f"   ✅ All ATP calculations correct (ATP = available + incoming)")
            
            # Check structure of first row
            if len(rows) > 0:
                sample = rows[0]
                by_entity = sample.get('by_entity', [])
                print(f"   ✓ Sample product: {sample.get('product_name')}")
                print(f"   ✓ Entities with stock: {len(by_entity)}")
                
                if len(by_entity) > 0:
                    first_entity = by_entity[0]
                    by_warehouse = first_entity.get('by_warehouse', [])
                    print(f"   ✓ Warehouses for first entity: {len(by_warehouse)}")
                    print(f"   ✅ Status board structure is correct")
                    return True
        
        return False
    
    def test_subfase14_status_board_entity_filter(self, role):
        """Test inventory status board with entity filter"""
        token = self.tokens.get(role)
        if not token:
            print(f"⚠️  Skipping status board entity filter test for {role} - no token")
            return False
        
        print(f"\n🔍 Testing Sub-fase 1.4: Status Board Entity Filter for {role}")
        
        ksc_id = self.entities.get('KSC')
        if not ksc_id:
            print(f"   ⚠️  KSC entity not found")
            return False
        
        success, response = self.run_test(
            "Sub-fase 1.4: Status Board filtered by KSC",
            "GET",
            f"api/inventory/status-board?owner_entity_id={ksc_id}",
            200,
            token=token,
            description="Get status board filtered by KSC entity"
        )
        
        if success and isinstance(response, list):
            rows = response
            print(f"   ✓ Found {len(rows)} products for KSC")
            
            # Verify all rows have KSC in by_entity
            for row in rows:
                by_entity = row.get('by_entity', [])
                entity_ids = [e.get('entity_id') for e in by_entity]
                if ksc_id not in entity_ids and len(by_entity) > 0:
                    print(f"   ❌ Product {row.get('product_name')} doesn't have KSC in by_entity")
                    return False
            
            print(f"   ✅ Entity filter working correctly")
            return True
        
        return False
    
    def test_subfase14_permissions(self):
        """Test Sub-fase 1.4 endpoints with different roles"""
        print(f"\n🔍 Testing Sub-fase 1.4: Permission Checks")
        
        # Test roles: sales, manager, warehouse, admin
        test_roles = ['sales', 'manager', 'warehouse', 'admin']
        
        # Login all roles
        role_logins = {
            'sales': ('sales@kainnusantara.id', 'demo12345'),
            'manager': ('manager@kainnusantara.id', 'demo12345'),
            'warehouse': ('warehouse@kainnusantara.id', 'demo12345'),
            'admin': ('admin@kainnusantara.id', 'demo12345')
        }
        
        for role, (email, password) in role_logins.items():
            if role not in self.tokens:
                self.test_login(email, password, role)
        
        all_success = True
        
        # Test preview-allocation (requires order:view)
        for role in test_roles:
            token = self.tokens.get(role)
            if not token:
                continue
            
            success, _ = self.run_test(
                f"Sub-fase 1.4: preview-allocation permission for {role}",
                "POST",
                "api/sales-orders/preview-allocation",
                200,
                data={
                    "entity_id": self.entities.get('KSC', ''),
                    "items": [{"product_id": self.products[0].get('id') if self.products else '', "quantity": 10, "unit": "meter"}]
                },
                token=token,
                description=f"Check {role} can access preview-allocation"
            )
            if not success:
                all_success = False
        
        # Test status-board (requires product:view)
        for role in test_roles:
            token = self.tokens.get(role)
            if not token:
                continue
            
            success, _ = self.run_test(
                f"Sub-fase 1.4: status-board permission for {role}",
                "GET",
                "api/inventory/status-board",
                200,
                token=token,
                description=f"Check {role} can access status-board"
            )
            if not success:
                all_success = False
        
        if all_success:
            print(f"   ✅ All roles have correct permissions for Sub-fase 1.4 endpoints")
        else:
            print(f"   ❌ Some roles have permission issues")
        
        return all_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print(f"📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for fail in self.failed_tests:
                error_msg = fail.get('error', f"Expected {fail.get('expected')}, got {fail.get('actual')}")
                print(f"  - {fail['test']}: {error_msg} ({fail['endpoint']})")
        
        print("="*60)


def main():
    print("="*60)
    print("🧪 KAIN NUSANTARA API TEST SUITE - SUB-FASE 1.4 ATP & FULFILLMENT MODES")
    print("="*60)
    
    tester = KainNusantaraAPITester()
    
    # Test root endpoint
    print("\n📍 TESTING ROOT ENDPOINT")
    print("-"*60)
    tester.test_root()
    
    # Test login as admin
    print("\n📍 TESTING AUTHENTICATION")
    print("-"*60)
    if not tester.test_login("admin@kainnusantara.id", "demo12345", "admin"):
        print("❌ Admin login failed, cannot proceed with tests")
        return 1
    
    # Load entities and products
    print("\n📍 LOADING ENTITIES AND PRODUCTS")
    print("-"*60)
    if not tester.load_entities_and_products("admin"):
        print("❌ Failed to load entities and products")
        return 1
    
    # SUB-FASE 1.4: ATP & FULFILLMENT MODES TESTS
    print("\n" + "="*60)
    print("🎯 SUB-FASE 1.4: ATP & FULFILLMENT MODES TESTS")
    print("="*60)
    
    # Test 1: preview-allocation - from_stock
    print("\n📍 TEST 1: Preview Allocation - from_stock")
    print("-"*60)
    tester.test_subfase14_preview_allocation_from_stock("admin")
    
    # Test 2: preview-allocation - from_incoming
    print("\n📍 TEST 2: Preview Allocation - from_incoming")
    print("-"*60)
    tester.test_subfase14_preview_allocation_from_incoming("admin")
    
    # Test 3: preview-allocation - backorder
    print("\n📍 TEST 3: Preview Allocation - backorder")
    print("-"*60)
    tester.test_subfase14_preview_allocation_backorder("admin")
    
    # Test 4: preview-allocation - inter_company
    print("\n📍 TEST 4: Preview Allocation - inter_company")
    print("-"*60)
    tester.test_subfase14_preview_allocation_inter_company("admin")
    
    # Test 5: inventory status board
    print("\n📍 TEST 5: Inventory Status Board")
    print("-"*60)
    tester.test_subfase14_inventory_status_board("admin")
    
    # Test 6: status board entity filter
    print("\n📍 TEST 6: Status Board Entity Filter")
    print("-"*60)
    tester.test_subfase14_status_board_entity_filter("admin")
    
    # Test 7: permissions for all roles
    print("\n📍 TEST 7: Permission Checks (all roles)")
    print("-"*60)
    tester.test_subfase14_permissions()
    
    # Print summary
    tester.print_summary()
    
    # Return exit code
    return 0 if tester.tests_passed == tester.tests_run else 1


if __name__ == "__main__":
    sys.exit(main())
