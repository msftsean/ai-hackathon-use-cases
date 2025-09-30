# Test Conversations for Virtual Citizen Assistant Demo

## Conversation 1: Trash Pickup Inquiry
**User**: "Hi, when is my next trash pickup?"  
**Expected Response**: "I'd be happy to help you with your trash pickup schedule! To provide accurate information, I'll need your address. Could you please provide your street address?"

**User**: "123 Oak Street"  
**Expected Response**: "Based on your address at 123 Oak Street (odd-numbered), your trash pickup days are Monday and Thursday. Your next pickup is scheduled for Monday, October 7th. Please have your bins out by 7:00 AM. Remember to use city-approved containers and separate recyclables from regular trash."

## Conversation 2: Business Permit Application  
**User**: "How do I get a permit for my food truck?"  
**Expected Response**: "To operate a food truck in NYC, you'll need several permits:

**Mobile Food Vendor License**: 
- Submit Form BP-101 to the Department of Health
- Required documents: business registration, insurance certificate, vehicle inspection
- Processing time: 10-15 business days
- Fee: $200 annually

**Additional Requirements**:
- Fire Department inspection for propane equipment
- Department of Consumer Affairs vendor permit
- Parking permits for specific locations

You can apply online at nyc.gov/permits or visit the Business Services office at 253 Broadway, 9th Floor. Would you like information about any specific requirement?"

## Conversation 3: Emergency Alert Check
**User**: "Are there any weather alerts for today?"  
**Expected Response**: "I've checked the current emergency alerts for NYC. There are no active weather emergencies at this time. However, there's a Winter Weather Advisory in effect from 6 PM tonight through 10 AM tomorrow, with light snow expected (2-4 inches).

**Recommendations**:
- Use caution when traveling tonight and tomorrow morning
- Allow extra time for commutes
- Follow @NYCEmergencyMgmt on social media for updates

Would you like information about snow removal schedules or warming center locations?"

## Conversation 4: Park Information
**User**: "What time does Central Park close?"  
**Expected Response**: "Central Park is open daily from 6:00 AM to 1:00 AM. The park features many amenities including:

- Multiple playgrounds and sports courts
- Walking and running paths
- Lakes for boating (seasonal)
- Designated dog runs
- Popular attractions like Bethesda Fountain and Strawberry Fields

**Important Notes**:
- Some areas may have different hours
- Bicycles are restricted on walking paths during peak hours (10 AM-3 PM and 7 PM-10 PM on weekdays)
- The Central Park Zoo has separate hours and admission fees

Is there a specific area or activity you're interested in?"

## Conversation 5: Follow-up Questions
**User**: "I asked about trash pickup earlier. What about recycling?"  
**Expected Response**: "Great follow-up question! Your recycling pickup follows the same schedule as your regular trash - Monday and Thursday for your odd-numbered address at 123 Oak Street.

**NYC Recycling Guidelines**:
- **What to recycle**: Paper, cardboard, metal cans, glass bottles/jars, plastic containers (symbols 1-7)
- **How to prepare**: Rinse containers, remove food residue, no need to remove labels
- **Collection**: Use blue bins or clear bags, keep items loose (no plastic bags)

**What NOT to recycle**:
- Plastic bags (return to participating stores)
- Electronics (special collection events)
- Batteries (drop-off locations available)

Your next recycling pickup is the same as trash: Monday, October 7th by 7:00 AM."

## Conversation 6: Complex Multi-Service Query
**User**: "I'm moving to NYC next month. What do I need to know about city services?"  
**Expected Response**: "Welcome to NYC! Here's a comprehensive guide for new residents:

**Essential Services Setup**:
1. **Trash & Recycling**: Pickup schedule depends on your address (odd/even system)
2. **Emergency Alerts**: Sign up for NotifyNYC at nyc.gov/notifynyc
3. **Parking**: Get familiar with alternate side parking rules
4. **311 Service**: Call 311 for any city service questions

**Important Registrations**:
- Voter registration
- School enrollment (if you have children)
- Benefits applications (if eligible)

**Resources**:
- NYC.gov for online services
- Local community boards for neighborhood info
- Public libraries for free services and programs

Would you like specific information about any of these services, or do you have questions about a particular neighborhood?"

## Error Handling Examples

**User**: "When does the subway run to Mars?"  
**Expected Response**: "I understand you're asking about transportation, but I can only provide information about NYC public services and transportation within the city. For NYC subway information, the MTA system operates 24/7 with some service modifications during overnight hours. 

For current service status, visit mta.info or call 511. Is there something specific about NYC transportation I can help you with?"

**User**: "Fix my broken sink"  
**Expected Response**: "I can't directly fix plumbing issues, but I can help you find the right resources:

**For Tenant Issues**:
- Contact your landlord or building management first
- If unresponsive, call 311 to report housing maintenance violations

**For Homeowners**:
- You'll need to hire a licensed plumber
- Check nyc.gov for licensed contractor databases

**Emergency Situations**:
- If there's flooding or a major leak, call 911
- For water main breaks on the street, call 311

Would you like information about tenant rights or how to report housing violations?"