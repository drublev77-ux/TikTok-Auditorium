#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================
## user_problem_statement: TikTok Auditorium (mobile MVP) — Phase 0-1 backend foundation (health, orgs/projects CRUD, manual import)
## backend:
##   - task: "Phase 0-1: Core API (health, orgs, projects, manual imports)"
##     implemented: true
##     working: true
##     file: "/app/backend/server.py"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##       - working: "NA"
##         agent: "main"
##         comment: "Implemented /api/health, /api/orgs (create/list), /api/projects (create/list/get), /api/imports/manual with optional csv_base64 parsing. Needs curl-based verification."
##       - working: true
##         agent: "testing"
##         comment: "✅ ALL TESTS PASSED: Comprehensive testing completed using both Python requests and curl. Health endpoint returns ok=true/mongo=true. Orgs CRUD working (create/list). Projects CRUD working (create/list/get by ID). Manual imports working with items array and CSV base64. Error handling working correctly for invalid project_id (400) and invalid CSV (400/404). All 10 test cases passed successfully. Backend Phase 0-1 is fully functional."
## frontend:
##   - task: "Phase 0-1: App shell (tabs + projects UI + i18n)"
##     implemented: true
##     working: true
##     file: "/app/frontend/app/*"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##       - working: "NA"
##         agent: "main"
##         comment: "Implemented expo-router navigation: Projects list, Create Project form, selected project persisted, Tabs layout (Dashboard/Audience/Competitors/Creators/Planner/Analytics/Settings), RU+EN i18n with persisted language setting. Needs UI testing."
##       - working: true
##         agent: "testing"
##         comment: "✅ MOBILE UI TESTS PASSED: Comprehensive testing on iPhone 13 dimensions (390x844). Projects screen loads correctly with existing projects displayed. Create project flow works - navigation, form filling (org name, project name, timezone), language toggle (RU/EN), and save functionality all operational. Project creation successful and projects appear in list. Tab navigation functional (Dashboard, Settings, etc.). Language switching in Settings tab works correctly with UI text updating. Dashboard Projects button successfully returns to projects list. All core mobile UI functionality working as expected. Minor: Multiple 'EN' elements cause selector conflicts but doesn't affect functionality."
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 1
##   run_ui: false
## test_plan:
##   current_focus:
##     - "Phase 0-1: App shell (tabs + projects UI + i18n)"
##   stuck_tasks: []
##   test_all: false
##   test_priority: "high_first"
## agent_communication:
##   - agent: "main"
##     message: "Please test backend endpoints via curl: /api/health, create/list org, create/list/get project, manual import with items and csv_base64. Ensure ObjectId handling and CSV parsing errors are clear."
##   - agent: "testing"
##     message: "✅ BACKEND TESTING COMPLETE: All Phase 0-1 endpoints are working perfectly. Created comprehensive test suite (/app/backend_test.py) and verified all functionality with both Python requests and curl commands. Health endpoint operational, CRUD operations for orgs/projects working, manual imports with items array and CSV parsing functional, error handling robust. Backend is ready for production. No issues found."
##   - agent: "main"
##     message: "Re-run UI tests now that web preview loads. Mobile dims: iPhone 13 390x844. Test: 1) / loads Projects screen 2) Click 'Создать проект' -> create screen 3) Fill form, switch to EN, save 4) Verify project in list 5) Tap project -> Tabs dashboard 6) Settings tab language toggle RU/EN 7) Dashboard Projects button return."
##   - agent: "testing"
##     message: "✅ MOBILE UI TESTING COMPLETE: All requested tests passed successfully on iPhone 13 dimensions. Projects screen loads with existing projects, create project flow fully functional (form filling, language selection, save), new projects appear in list, tab navigation works, language switching operational in Settings with UI updates, Dashboard Projects button returns to projects list. Core mobile functionality working perfectly. Ready for production use."
