# Appeal Functionality Implementation Summary

## Task: 14.2 实现异议申请功能

### Requirements Addressed
- **Requirement 8.2**: 教师对评分结果有异议时，系统支持提交异议申请
- **Requirement 8.3**: 教师提交异议时，系统要求填写异议理由

### Implementation Overview

#### 1. UI Components Added

**Appeal Button** (in scoring record section)
- Location: MaterialSubmission.vue, scoring record footer
- Visibility: Only shown when:
  - Record is not confirmed (`is_confirmed === false`)
  - No existing appeal (`has_appeal === false`)
- Styling: Orange button with icon (📝 提交异议)

**Appeal Dialog** (modal dialog)
- Location: MaterialSubmission.vue, bottom of template
- Features:
  - Displays current scoring information (file name, score, grade)
  - Text area for appeal reason input
  - Real-time character count (minimum 20 characters required)
  - Submit and Cancel buttons
  - Form validation

#### 2. Data State Management

```typescript
// New reactive state variables
const showAppealDialog = ref(false);
const currentAppealRecord = ref<any>(null);
const submittingAppeal = ref(false);
const appealForm = ref({
  reason: ''
});
```

#### 3. Functions Implemented

**openAppealDialog(record)**
- Opens the appeal dialog
- Initializes form with selected record data
- Clears previous form input

**closeAppealDialog()**
- Closes the appeal dialog
- Clears form data
- Resets state

**validateAppealReason()**
- Validates appeal reason length (minimum 20 characters)
- Returns boolean indicating validity

**submitAppeal()**
- Validates form before submission
- Sends POST request to `/api/scoring/appeals`
- Handles success and error responses
- Updates record state after successful submission
- Refreshes submission list

#### 4. API Integration

**Endpoint**: `POST /api/scoring/appeals`

**Request Body**:
```json
{
  "scoring_record_id": 123,
  "appeal_reason": "详细的异议理由..."
}
```

**Response**:
```json
{
  "message": "异议提交成功",
  "appeal_id": 456,
  "status": "pending"
}
```

#### 5. Styling

**Appeal Button Styles**:
- Background: Orange (#FF9800)
- Hover effect with shadow
- Responsive sizing

**Appeal Dialog Styles**:
- Modal overlay with semi-transparent background
- Centered dialog box (max-width: 600px)
- Smooth animations and transitions
- Grade-specific color coding for display

**Form Validation Styles**:
- Character count display with error state
- Disabled submit button when validation fails
- Visual feedback for form focus

#### 6. User Flow

1. Teacher views scoring results in MaterialSubmission component
2. If record is not confirmed and has no appeal, "提交异议" button appears
3. Teacher clicks button to open appeal dialog
4. Dialog displays:
   - File name
   - Current score
   - Current grade
   - Text area for appeal reason
5. Teacher enters appeal reason (minimum 20 characters)
6. Character count updates in real-time
7. Submit button becomes enabled when reason is valid
8. Teacher clicks submit
9. System sends appeal to backend
10. Success message displayed
11. Record marked as having appeal
12. Appeal badge replaces button
13. Submission list refreshed

#### 7. Validation Rules

- **Appeal Reason**: 
  - Minimum 20 characters
  - Cannot be empty or whitespace only
  - Trimmed before submission

- **Record Eligibility**:
  - Must not be confirmed
  - Must not have existing appeal
  - Must have valid scoring record ID

#### 8. Error Handling

- Network errors: Display error message with details
- Validation errors: Show appropriate error messages
- API errors: Display backend error details
- Form validation: Disable submit button until valid

#### 9. User Feedback

- Confirmation dialog before submission
- Success message after submission
- Error alerts for failures
- Loading state during submission
- Visual status indicators (appeal badge)

### Code Changes

**File**: `评教系统最终版/评教系统教师端/frontend/src/views/MaterialSubmission.vue`

**Changes**:
1. Added appeal dialog template section
2. Added appeal button in scoring record section
3. Added reactive state variables for appeal form
4. Added appeal-related functions (open, close, submit, validate)
5. Added comprehensive CSS styling for appeal UI

### Testing

**Test File**: `MaterialSubmission.appeal.test.ts`

**Test Coverage**:
- Appeal dialog opening/closing
- Form validation (minimum length, empty string)
- Submit button disabled state
- Appeal button visibility conditions
- Request/response format validation
- Error handling
- UI element display

### Compliance

✅ Requirement 8.2: Appeal submission functionality implemented
✅ Requirement 8.3: Appeal reason validation implemented (minimum 20 characters)
✅ Property 19: Appeal form validation working
✅ Property 20: Appeal submission notifies backend

### Integration Points

- Backend API: `/api/scoring/appeals` (POST)
- Database: ScoringAppeal table
- Review Manager: Handles appeal processing
- Notification: Admin notification on appeal submission

### Future Enhancements

1. Real-time appeal status updates
2. Appeal history view
3. Appeal response display
4. Appeal timeline tracking
5. Bulk appeal operations
6. Appeal analytics dashboard
