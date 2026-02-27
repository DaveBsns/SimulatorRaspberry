using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

// Please use using SBPScripts; directive to refer to or append the SBP library


namespace SBPScripts
{
    // Cycle Geometry Class - Holds Gameobjects pertaining to the specific bicycle
    [System.Serializable]
    public class CycleGeometry
    {
        public GameObject handles, lowerFork, fWheelVisual, RWheel, crank, lPedal, rPedal, fGear, rGear;
    }
    //Pedal Adjustments Class - Manipulates pedals and their positioning.  


    [System.Serializable]
    public class PedalAdjustments
    {
        public float crankRadius;
        public Vector3 lPedalOffset, rPedalOffset;
        public float pedalSpeed;
    }
    // Wheel Friction Settings Class - Uses Physics Materials and Physics functions to control the 
    // static / dynamic slipping of the wheels 
    [System.Serializable]
    public class WheelFrictionSettings
    {
        public PhysicMaterial fPhysicMaterial, rPhysicMaterial;
        public Vector2 fFriction, rFriction;
    }
    public class BicycleController : MonoBehaviour
    {
        // Steering Models
        public enum SteeringModel
        {
            Baseline,          // θs = θh only
            Nonlinear,         // θs = θh + α ⋅ sin(θr)
            VelocityWeighted,  // θs = θh ⋅ w(v) + θr ⋅ (1 - w(v))
        }

        [Header("Steering Integration Model Settings")]
        public SteeringModel selectedSteeringModel = SteeringModel.Baseline;

        // These are now private constants, not adjustable in UI
        private const float BASELINE_SENSITIVITY = 1f;
        private const float NONLINEAR_GAIN = 0.25f;
        private const float NONLINEAR_SENSITIVITY = 0.9f;
        private const float VELOCITY_MODEL_CONSTANT = 1.5f;
        private const float VELOCITY_SENSITIVITY = 0.85f;

        // Brake incline adjustment

        [Header("Incline Override Settings")]
        [Tooltip("Enable or disable incline override based on braking/acceleration.")]
        public bool useInclineOverride = true;


        [Header("Brake-based Incline Control")]
        [Range(0f, 10f)] public float brakeInclineStep = 3f;
        [Range(0.01f, 1f)] public float inclineResetSpeed = 0.25f;

        private float brakeInclineAdjustment = 0f;
        private bool isBraking = false;
        private float inclineResetVelocity = 0f;

        [Header("Accel-based Incline Control")]
        [Range(0f, 10f)] public float accelInclineStep = 1f;
        [Range(0.01f, 1f)] public float accelSensitivityThreshold = 75f;

        private float accelInclineAdjustment = 0f;
        private bool isAccelerating = false;
        private float accelResetVelocity = 0f;
        private float currentSpeed;


        [Header("Fan Settings")]
        public float speedThresholdForFan = 0.5f;  // Minimum speed to turn fan on
        public float fanSmoothSpeed = 5f;         // How fast fan value smooths
        [Header("Wind Settings")]
        public float windMultiplier = 2f;   // Increase for stronger wind
        public float topBikeSpeed = 15f;    // Used for speed scaling


        // Scriptable object which stores the bicycle data
        public BikeDataSO bikeData;
        private float backwheelSpeed;
        private float pedalSpeed;
        private float rizerSteering;
        private float espBno;
        private float espBrake;
        private float espRoll;
        private int bleFan;             // Write
        private int bleIncline;         // Write
        private int diretoResistance;   // Write
        public float brakeDefaultValue = 0f;
        public float steeringAngle;
        public bool usingOldVersion;

        public int maxLeanAngle = 10; // maxLeanAngle is the maximum angle the bike can lean
        public int leanLerpSpeed = 1; // representing the speed at which the bicycle's lean angle is interpolated towards the target lean angle

        public CycleGeometry cycleGeometry;
        public GameObject fPhysicsWheel, rPhysicsWheel;
        public WheelFrictionSettings wheelFrictionSettings;

        // Curve of Power Exerted over Input time by the cyclist
        // This class sets the physics materials on to the
        // tires of the bicycle. F Friction pertains to the front tire friction and R Friction to
        // the rear. They are of the Vector2 type. X field edits the static friction
        // information and Y edits the dynamic friction. Please keep the values over 0.5.
        // For more information, please read the commented scripts.
        public AnimationCurve accelerationCurve;
        [Tooltip("Steer Angle over Speed")]
        public AnimationCurve steerAngle;
        public float axisAngle;
        // Defines the leaning curve of the bicycle
        public AnimationCurve leanCurve;
        // The slider refers to the ratio of Relaxed mode to Top Speed. 
        // Torque is a physics based function which acts as the actual wheel driving force.
        public float torque, topSpeed;
        [Range(0.1f, 0.9f)]
        [Tooltip("Ratio of Relaxed mode to Top Speed")]
        // public float relaxedSpeed;
        public float reversingSpeed;
        public Vector3 centerOfMassOffset;
        [HideInInspector]
        public bool isReversing, isAirborne, stuntMode;
        // Controls Cycle sway from left to right.
        // The degree of cycle waddling side to side upon pedaling.
        // Higher values correspond to higher waddling. This property also affects
        // character IK. 

        [Range(0, 8)]
        public float oscillationAmount;
        // Following the natural movement of a cyclist, the
        // oscillation of the cycle from side to side also affects the steering to a certain
        // extent. This value refers to the counter steer upon cycle oscillation. Higher
        // values correspond to a higher percentage of the oscillation being transferred
        // to the steering handles. 

        [Range(0, 1)]
        public float oscillationAffectSteerRatio;
        float oscillationSteerEffect;
        [HideInInspector]
        public float cycleOscillation;
        [HideInInspector]
        public Rigidbody rb, fWheelRb, rWheelRb;
        float turnAngle;
        float xQuat, zQuat;
        [HideInInspector]
        public float crankSpeed, crankCurrentQuat, crankLastQuat, restingCrank;
        public PedalAdjustments pedalAdjustments;
        [HideInInspector]
        public float turnLeanAmount;
        RaycastHit hit;
        [HideInInspector]
        public float customSteerAxis, customLeanAxis, customAccelerationAxis, rawCustomAccelerationAxis;
        bool isRaw, sprint;
        [HideInInspector]
        public bool wheelieInput;
        [HideInInspector]
        public float wheeliePower;
        public bool wheelieToggle;
        [HideInInspector]
        public int bunnyHopInputState;
        [HideInInspector]
        public float currentTopSpeed, pickUpSpeed;
        Quaternion initialLowerForkLocalRotaion, initialHandlesRotation;
        ConfigurableJoint fPhysicsWheelConfigJoint, rPhysicsWheelConfigJoint;
        // Ground Conformity refers to vehicles that do not need a gyroscopic force to keep them upright.
        // For non-gyroscopic wheel systems like the tricycle,
        // enabling ground conformity ensures that the tricycle is not always upright and
        // follows the curvature of the terrain. 
        public bool groundConformity;
        RaycastHit hitGround;
        Vector3 theRay;
        float groundZ;
        JointDrive fDrive, rYDrive, rZDrive;
        // Attempts to Reduce/eliminate bouncing of the bicycle after a fall impact 
        public bool inelasticCollision;
        [HideInInspector]
        public Vector3 lastVelocity, deceleration, lastDeceleration;
        int impactFrames;

        public float topSpeedMax;

        private float GetCombinedSteering(float steerInputDeg, float rollInputDeg, float currentSpeed)
        {
            float steerNorm = Mathf.Clamp(steerInputDeg / 17f, -1f, 1f);
            float rollNorm = Mathf.Clamp(rollInputDeg / 7f, -1f, 1f);

            float output = 0f;
            float sensitivity = 1f;

            switch (selectedSteeringModel)
            {
                case SteeringModel.Baseline:
                    output = steerNorm;
                    sensitivity = BASELINE_SENSITIVITY;
                    break;

                case SteeringModel.Nonlinear:
                    float sinComponent = Mathf.Sin(rollNorm * Mathf.PI / 2f);
                    output = steerNorm + NONLINEAR_GAIN * sinComponent;
                    sensitivity = NONLINEAR_SENSITIVITY;
                    break;

                case SteeringModel.VelocityWeighted:
                    float speedNorm = currentSpeed / VELOCITY_MODEL_CONSTANT;
                    float w = currentSpeed * currentSpeed / (currentSpeed * currentSpeed + VELOCITY_MODEL_CONSTANT);
                    output = w * steerNorm + (1f - w) * rollNorm;
                    sensitivity = VELOCITY_SENSITIVITY;
                    break;
            }

            return Mathf.Clamp(-output * 3f * sensitivity, -3f, 3f);
        }

        void Awake()
        {
            transform.rotation = Quaternion.Euler(0, transform.rotation.eulerAngles.y, 0);
        }


        void Start()
        {

            bikeData.bleFan = 0;
            bikeData.bleIncline = 0;

            topSpeedMax = 0.0f;

            // Braking
            //brakeDefaultValue = bikeData.espBrake;

            rb = GetComponent<Rigidbody>();
            rb.maxAngularVelocity = Mathf.Infinity;

            fWheelRb = fPhysicsWheel.GetComponent<Rigidbody>();
            fWheelRb.maxAngularVelocity = Mathf.Infinity;

            rWheelRb = rPhysicsWheel.GetComponent<Rigidbody>();
            rWheelRb.maxAngularVelocity = Mathf.Infinity;

            currentTopSpeed = topSpeed;

            initialHandlesRotation = cycleGeometry.handles.transform.localRotation;
            initialLowerForkLocalRotaion = cycleGeometry.lowerFork.transform.localRotation;

            fPhysicsWheelConfigJoint = fPhysicsWheel.GetComponent<ConfigurableJoint>();
            rPhysicsWheelConfigJoint = rPhysicsWheel.GetComponent<ConfigurableJoint>();
        }









        void FixedUpdate()
        {

            //Physics based Steering Control.
            fPhysicsWheel.transform.rotation = Quaternion.Euler(transform.rotation.eulerAngles.x, transform.rotation.eulerAngles.y + customSteerAxis * steerAngle.Evaluate(rb.velocity.magnitude) + oscillationSteerEffect, 0);
            fPhysicsWheelConfigJoint.axis = new Vector3(1, 0, 0);

            //cache rb velocity
            float currentSpeed = rb.velocity.magnitude;

            //Power Control. Wheel Torque + Acceleration curves
            // The currentTopSpeed is adjusted using Mathf.Lerp to smoothly interpolate between its current value and the top speed with a factor. 
            // The interpolation factor is Time.deltaTime, ensuring smooth and frame-rate-independent transitions.
            //old currentTopSpeed = Mathf.Lerp(currentTopSpeed, topSpeed * 0.6f, Time.deltaTime);
            //new 
            currentTopSpeed = topSpeed;


            // only apply torque if the cyclist is using the pedals
            //oldif (currentSpeed < currentTopSpeed && rawCustomAccelerationAxis > 0 && bikeData.pedalSpeed > 0.2f)
            // rWheelRb.AddTorque(transform.right * torque * customAccelerationAxis);
            if (rawCustomAccelerationAxis > 0 && bikeData.pedalSpeed > 0.2f)
            {
                float speedFactor = 1f - Mathf.Clamp01(currentSpeed / topSpeed);
                float dynamicTorque = torque * rawCustomAccelerationAxis * speedFactor;

                rWheelRb.AddTorque(transform.right * dynamicTorque);
            }



            // only apply forward force if the cyclist is using the pedals
            //oldif (currentSpeed < currentTopSpeed && rawCustomAccelerationAxis > 0 && bikeData.pedalSpeed > 0.2f)
            // rb.AddForce(transform.forward * accelerationCurve.Evaluate(customAccelerationAxis));
            if (rawCustomAccelerationAxis > 0 && bikeData.pedalSpeed > 0.2f)
            {
                float speedFactor = 1f - Mathf.Clamp01(currentSpeed / topSpeed);
                float accelForce = accelerationCurve.Evaluate(Mathf.Clamp01(rawCustomAccelerationAxis));

                rb.AddForce(transform.forward * accelForce * rawCustomAccelerationAxis * speedFactor);
            }





            // Triggered when the roll moves the bike backwards
            if (currentSpeed < reversingSpeed && rawCustomAccelerationAxis < 0 && bikeData.espRoll > 0)
                rb.AddForce(-transform.forward * accelerationCurve.Evaluate(customAccelerationAxis) * 0.5f);

            if (transform.InverseTransformDirection(rb.velocity).z < 0)
                isReversing = true;
            else
                isReversing = false;

            if (rawCustomAccelerationAxis < 0 && isReversing == false)
                rb.AddForce(-transform.forward * accelerationCurve.Evaluate(customAccelerationAxis) * 2);

            // Center of Mass handling
            rb.centerOfMass = Vector3.zero + centerOfMassOffset;

            //Handles
            cycleGeometry.handles.transform.localRotation = Quaternion.Euler(0, customSteerAxis * steerAngle.Evaluate(currentSpeed) + oscillationSteerEffect * 5, 0) * initialHandlesRotation;

            //LowerFork
            cycleGeometry.lowerFork.transform.localRotation = Quaternion.Euler(0, customSteerAxis * steerAngle.Evaluate(currentSpeed) + oscillationSteerEffect * 5, customSteerAxis * -axisAngle) * initialLowerForkLocalRotaion;

            //FWheelVisual
            xQuat = Mathf.Sin(Mathf.Deg2Rad * (transform.rotation.eulerAngles.y));
            zQuat = Mathf.Cos(Mathf.Deg2Rad * (transform.rotation.eulerAngles.y));
            cycleGeometry.fWheelVisual.transform.rotation = Quaternion.Euler(xQuat * (customSteerAxis * -axisAngle), customSteerAxis * steerAngle.Evaluate(currentSpeed) + oscillationSteerEffect * 5, zQuat * (customSteerAxis * -axisAngle));
            cycleGeometry.fWheelVisual.transform.GetChild(0).transform.localRotation = cycleGeometry.RWheel.transform.rotation;

            //Crank
            if (bikeData.pedalSpeed < 0.2f)
            {
                bikeData.pedalSpeed = 0;
            }

            crankSpeed += bikeData.pedalSpeed * 360 * Time.deltaTime;
            crankSpeed %= 360;
            cycleGeometry.crank.transform.localRotation = Quaternion.Euler(crankSpeed, 0, 0);
            crankLastQuat = crankCurrentQuat;

            // this part probably won't change - the pedals move relatively to the crank, and we need to move the crank
            //Pedals
            cycleGeometry.lPedal.transform.localPosition = pedalAdjustments.lPedalOffset + new Vector3(0, Mathf.Cos(Mathf.Deg2Rad * (crankSpeed + 180)) * pedalAdjustments.crankRadius, Mathf.Sin(Mathf.Deg2Rad * (crankSpeed + 180)) * pedalAdjustments.crankRadius);
            cycleGeometry.rPedal.transform.localPosition = pedalAdjustments.rPedalOffset + new Vector3(0, Mathf.Cos(Mathf.Deg2Rad * (crankSpeed)) * pedalAdjustments.crankRadius, Mathf.Sin(Mathf.Deg2Rad * (crankSpeed)) * pedalAdjustments.crankRadius);

            //FGear
            if (cycleGeometry.fGear != null)
                cycleGeometry.fGear.transform.rotation = cycleGeometry.crank.transform.rotation;
            //RGear
            if (cycleGeometry.rGear != null)
                cycleGeometry.rGear.transform.rotation = rPhysicsWheel.transform.rotation;

            //CycleOscillation
            if ((sprint && currentSpeed > 5 && isReversing == false))
                pickUpSpeed += Time.deltaTime * 2;
            else
                pickUpSpeed -= Time.deltaTime * 2;

            pickUpSpeed = Mathf.Clamp(pickUpSpeed, 0.1f, 1);

            cycleOscillation = -Mathf.Sin(Mathf.Deg2Rad * (crankSpeed + 90)) * (oscillationAmount * (Mathf.Clamp(currentTopSpeed / currentSpeed, 1f, 1.5f))) * pickUpSpeed;
            turnLeanAmount = -leanCurve.Evaluate(customLeanAxis) * Mathf.Clamp(currentSpeed * 0.1f, 0, 1);
            oscillationSteerEffect = cycleOscillation * Mathf.Clamp01(customAccelerationAxis) * (oscillationAffectSteerRatio * (Mathf.Clamp(topSpeed / currentSpeed, 1f, 1.5f)));

            //FrictionSettings
            wheelFrictionSettings.fPhysicMaterial.staticFriction = wheelFrictionSettings.fFriction.x;
            wheelFrictionSettings.fPhysicMaterial.dynamicFriction = wheelFrictionSettings.fFriction.y;
            wheelFrictionSettings.rPhysicMaterial.staticFriction = wheelFrictionSettings.rFriction.x;
            wheelFrictionSettings.rPhysicMaterial.dynamicFriction = wheelFrictionSettings.rFriction.y;

            if (Physics.Raycast(fPhysicsWheel.transform.position, Vector3.down, out hit, Mathf.Infinity))
                if (hit.distance < 0.5f)
                {
                    Vector3 velf = fPhysicsWheel.transform.InverseTransformDirection(fWheelRb.velocity);
                    velf.x *= Mathf.Clamp01(1 / (wheelFrictionSettings.fFriction.x + wheelFrictionSettings.fFriction.y));
                    fWheelRb.velocity = fPhysicsWheel.transform.TransformDirection(velf);
                }
            if (Physics.Raycast(rPhysicsWheel.transform.position, Vector3.down, out hit, Mathf.Infinity))
                if (hit.distance < 0.5f)
                {
                    Vector3 velr = rPhysicsWheel.transform.InverseTransformDirection(rWheelRb.velocity);
                    velr.x *= Mathf.Clamp01(1 / (wheelFrictionSettings.rFriction.x + wheelFrictionSettings.rFriction.y));
                    rWheelRb.velocity = rPhysicsWheel.transform.TransformDirection(velr);
                }

            //Impact sensing
            deceleration = (fWheelRb.velocity - lastVelocity) / Time.fixedDeltaTime;
            lastVelocity = fWheelRb.velocity;
            impactFrames--;
            impactFrames = Mathf.Clamp(impactFrames, 0, 15);
            if (deceleration.y > 200 && lastDeceleration.y < -1)
                impactFrames = 30;
            lastDeceleration = deceleration;
            if (impactFrames > 0 && inelasticCollision)
            {
                fWheelRb.velocity = new Vector3(fWheelRb.velocity.x, -Mathf.Abs(fWheelRb.velocity.y), fWheelRb.velocity.z);
                rWheelRb.velocity = new Vector3(rWheelRb.velocity.x, -Mathf.Abs(rWheelRb.velocity.y), rWheelRb.velocity.z);
            }

            // Setting the Main Rotational movements of the bicycle
            float leanAngle = customLeanAxis * maxLeanAngle;
            Quaternion targetRotation = Quaternion.Euler(transform.rotation.eulerAngles.x, transform.rotation.eulerAngles.y, turnLeanAmount + cycleOscillation + GroundConformity(groundConformity) + leanAngle);
            transform.rotation = Quaternion.Lerp(transform.rotation, targetRotation, leanLerpSpeed * Time.deltaTime);
        }



        void Update()
        {

            float currentSpeed = rb.velocity.magnitude;

            if (currentSpeed > topSpeedMax)
            {
                topSpeedMax = currentSpeed;
            }

            // Bicycle data from bike data scriptable object
            backwheelSpeed = bikeData.backwheelSpeed;
            pedalSpeed = bikeData.pedalSpeed;
            rizerSteering = bikeData.rizerSteering;
            espBno = bikeData.espBno;
            espBrake = bikeData.espBrake;
            espRoll = bikeData.espRoll;
            steeringAngle = bikeData.steeringAngle;

            //Acceleration 
            /* if (pedalSpeed > 0.2f)
             {
                 rawCustomAccelerationAxis = backwheelSpeed * 0.5f;
             }*/
            //old rawCustomAccelerationAxis = Mathf.Clamp01(pedalSpeed);
            rawCustomAccelerationAxis = pedalSpeed;



            if (pedalSpeed > 0.3f && bikeData.bleFan == 0)
            {
                bikeData.bleFan = 1;
            }
            else if (pedalSpeed <= 0.1f && bikeData.bleFan > 0)
            {
                bikeData.bleFan = 0;
            }
            else
            {
                bikeData.bleFan = Math.Clamp((int)(currentSpeed * 7.5f), 0, 100);
            }


            // The following section determining the incline of the bike       
            // First determine the position of the front and rear wheels
            Vector3 fWheelPos = fPhysicsWheel.transform.position;
            Vector3 rWheelPos = rPhysicsWheel.transform.position;

            // Calculate the horizontal distance (x or z, depending on alignment) between the wheels
            float horizontalDistance = Vector3.Distance(new Vector3(fWheelPos.x, 0, fWheelPos.z), new Vector3(rWheelPos.x, 0, rWheelPos.z));

            // Calculate the vertical distance (y-axis difference)
            float verticalDistance = fWheelPos.y - rWheelPos.y;

            // Calculate the incline angle in radians, then convert to degrees
            int inclineAngle = (int)Math.Round(Mathf.Atan2(verticalDistance, horizontalDistance) * Mathf.Rad2Deg);

            // Apply the multiplier only to positive incline values
            int adjustedInclineAngle = inclineAngle > 0 ? inclineAngle * 2 : inclineAngle;

            // Clamp the incline value to the range -15 to 15
            //bikeData.bleIncline = Math.Clamp(adjustedInclineAngle, -15, 15);
            // --- Additional incline for braking ---
            float accelerationMagnitude = Mathf.Abs(rawCustomAccelerationAxis);


            // Braking
            //if (brakeDefaultValue <= 0) brakeDefaultValue = espBrake;
            /*float brakeValueUpper = brakeDefaultValue - 40;
            float brakeValueLower = brakeDefaultValue - 250;
            float brakeFactor = 0f;
            if (espBrake >= brakeValueUpper)
            {
                brakeFactor = 0f;
            }
            else if (espBrake <= brakeValueLower)
            {
                brakeFactor = 1f;
            }
            else
            {
                brakeFactor = Mathf.InverseLerp(brakeValueUpper, brakeValueLower, espBrake);
            }*/

            float brakeFactor = 0f;
            float deadZone = 7.5f;
            float fullBreakThreshold = 25f;

            float relativeBreak = espBrake;

            if (relativeBreak <= deadZone)
            {
                brakeFactor = 0f;
            }
            else if (relativeBreak >= fullBreakThreshold)
            {
                brakeFactor = 1f;
            }
            else
            {
                brakeFactor = Mathf.InverseLerp(deadZone, fullBreakThreshold, relativeBreak);
            }

            bikeData.brakeFactor = brakeFactor;

            // currentSpeed measures the speed of the bicycle in the forward direction
            if (brakeFactor > 0 && currentSpeed > 0)
            {
                rawCustomAccelerationAxis = -180 * brakeFactor;
            }

            // negative values for currentSpeed mean the bicycle is moving in the opposite direction
            else if (brakeFactor > 0 && currentSpeed < 0)
            {
                // Stop the bike from moving
                rb.velocity = new Vector3(0, 0, 0);
            }
            else if (espRoll != 0)
            {
                rawCustomAccelerationAxis = -espRoll * 150;
            }


            // Determine incline from geometry


            // --- Brake-based incline offset ---
            if (useInclineOverride)
            {
                // === Braking Incline Logic ===
                if (brakeFactor > 0.25f)
                {
                    brakeInclineAdjustment = -brakeInclineStep * 2f;
                    isBraking = true;
                }
                else if (brakeFactor > 0.15f)
                {
                    brakeInclineAdjustment = -brakeInclineStep;
                    isBraking = true;
                }
                else if (rawCustomAccelerationAxis > accelSensitivityThreshold && isBraking)
                {
                    // Reset brake incline when acceleration begins
                    brakeInclineAdjustment = Mathf.SmoothDamp(brakeInclineAdjustment, 0f, ref inclineResetVelocity, inclineResetSpeed);
                    if (Mathf.Abs(brakeInclineAdjustment) < 0.1f)
                    {
                        brakeInclineAdjustment = 0f;
                        isBraking = false;
                    }
                }

                // === Acceleration Incline Logic ===
                if (rawCustomAccelerationAxis > accelSensitivityThreshold)
                {
                    if (rawCustomAccelerationAxis > accelSensitivityThreshold * 1.5f)
                        accelInclineAdjustment = accelInclineStep * 2f;
                    else
                        accelInclineAdjustment = accelInclineStep;

                    isAccelerating = true;
                }
                else if (brakeFactor > 0.15f && isAccelerating)
                {
                    // Reset accel incline when braking starts
                    accelInclineAdjustment = Mathf.SmoothDamp(accelInclineAdjustment, 0f, ref accelResetVelocity, inclineResetSpeed);
                    if (Mathf.Abs(accelInclineAdjustment) < 0.1f)
                    {
                        accelInclineAdjustment = 0f;
                        isAccelerating = false;
                    }
                }

                // Final adjusted incline (combined with terrain)
                int finalIncline = Mathf.Clamp(adjustedInclineAngle + Mathf.RoundToInt(brakeInclineAdjustment + accelInclineAdjustment), -15, 15);
                bikeData.bleIncline = finalIncline;
            }
            else
            {
                // Use default incline only
                bikeData.bleIncline = Mathf.Clamp(adjustedInclineAngle, -15, 15);
            }

            //Debug.Log($"Angle: {espBrake} ,BrakeFactor: {brakeFactor}, Acceleration: {rawCustomAccelerationAxis}, backwheel: {backwheelSpeed}, Pedal speed {pedalSpeed}");

            // current bike speed : 

            //Leaning
            customLeanAxis = espBno * 0.5f;

            //Steering
            //customSteerAxis = steeringAngle * -0.1f;


            // Normalize both inputs
            /*float normLean = Mathf.Clamp(espBno / 3f, -1f, 1f);
            float normSteer = Mathf.Clamp(steeringAngle / 17f, -1f, 1f);

            float tiltWeight = 0.5f;

            // Blend based on tiltWeight (0 = full steering, 1 = full tilt)
            float combinedInput = tiltWeight * normLean + (1f - tiltWeight) * normSteer;

            // Final output scaled to your simulation needs (optional)
            customSteerAxis = combinedInput * -3f;*/


            float rawSteeringAngle = steeringAngle;  // in degrees
            float rawLeanAngle = espBno * 0.5f;      // adjust as needed

            customSteerAxis = GetCombinedSteering(rawSteeringAngle, rawLeanAngle, currentSpeed);


        }



        float GroundConformity(bool toggle)
        {
            if (toggle)
            {
                groundZ = transform.rotation.eulerAngles.z;
            }
            return groundZ;
        }
    }
}
