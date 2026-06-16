using System;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class UdpSender : MonoBehaviour
{
    [Header("Bike Data")]
    public BikeDataSO bikeData;

    [Header("UDP Settings")]
    public string serverIP = "127.0.0.1";
    public int serverPort = 12345;

    private UdpClient udpClient;
    private int lastBleFanValue;
    private float lastBleInclineValue;
    private float lastBleResistance;
    private float ble_resistance;

    [Header("Wind Simulation")]
    public float headWindSpeed = 5f;        // base wind speed (max)
    public float windResistanceFactor = 2f; // scales wind effect
    public float windSmoothTime = 0.3f;     // base smoothing duration
    public float topBikeSpeed = 10f;        // speed at which wind reaches max

    [Header("Dynamic Gusts / Tailwind")]
    public float gustStrength = 1.2f;         //3f max gust additional resistance
    public float gustFrequency = 0.6f;      // 0.7how fast gusts change
    public float tailwindMultiplier = 0.5f; // reduces resistance if moving with wind

    private float currentWindResistance = 0f;
    private float windVelocity = 0f;
    private float gustTimer = 0f;

    private void Start()
    {
        udpClient = new UdpClient();
    }

    private void OnDestroy()
    {
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }

    private void Update()
    {
        // 1️ Compute base resistance from incline, speed, brake
        float baseResistance = compute_resistance(bikeData.bleIncline, bikeData.currentBikeSpeed, bikeData.brakeFactor);

        // 2️ Compute target wind resistance with speed scaling
        float targetWindResistance = 0f;

        if (bikeData.currentBikeSpeed > 0.5f) // minimum speed threshold
        {
            float speedFactor = Mathf.Clamp01(bikeData.currentBikeSpeed / topBikeSpeed);

            // Base wind scaled by speed
            targetWindResistance = headWindSpeed * headWindSpeed * windResistanceFactor * speedFactor;

            // Dynamic gusts using Perlin noise, scaled by speed
            gustTimer += Time.deltaTime * gustFrequency;
            float gust = (Mathf.PerlinNoise(gustTimer, 0f) - 0.5f) * 2f * gustStrength * speedFactor;
            targetWindResistance += gust;

            // Tailwind effect if bike moving backward (simplified)
            if (bikeData.currentBikeSpeed < 0)
            {
                targetWindResistance *= tailwindMultiplier;
            }
        }


        // 3️ Adaptive smoothing based on speed
        float smoothTimeAdjusted = windSmoothTime / Mathf.Clamp(bikeData.currentBikeSpeed, 1f, topBikeSpeed);
        currentWindResistance = Mathf.SmoothDamp(
            currentWindResistance,
            targetWindResistance,
            ref windVelocity,
            smoothTimeAdjusted
        );

        // 4️ Apply to BLE resistance
        ble_resistance = baseResistance + currentWindResistance;
        ble_resistance = Mathf.Clamp(ble_resistance, 0, 100);

        // 5️ Send data if anything changed
        if (lastBleFanValue != bikeData.bleFan || lastBleInclineValue != bikeData.bleIncline || lastBleResistance != ble_resistance)
        {
            SendData(bikeData.bleFan, bikeData.bleIncline, ble_resistance);
            lastBleResistance = ble_resistance;
        }

        // 🔹 Optional debug
        Debug.Log($"Speed:{bikeData.currentBikeSpeed:F2}, Base:{baseResistance:F1}, Wind:{currentWindResistance:F1}, Total:{ble_resistance:F1}");
    }

    private float compute_resistance(float incline, float speed, float brake)
    {
        float inclineResistance;

        if (incline < 0)
            inclineResistance = (20 + incline * 2) / 2;
        else if (incline > 0)
            inclineResistance = (incline * 2 * 2.25f) + 10;
        else
            inclineResistance = 10;

        float speedFactor = 0.3f;
        float speedResistance = Mathf.Round(speed * speedFactor);

        float intermediateResistance = Mathf.Clamp(inclineResistance + speedResistance, 0, 100);

        float brakeResistance = Mathf.Round(brake * 400f);

        float totalResistance = Mathf.Clamp(Mathf.Round(intermediateResistance + brakeResistance), 0, 256);

        return totalResistance;
    }

    public void SendData(int currentBleFanValue, float currentBleInclineValue, float ble_resistance)
    {
        if (bikeData != null)
        {
            try
            {
                string jsonString = "{\"bleFan\":" + currentBleFanValue + ", \"bleIncline\": " + currentBleInclineValue + ", \"bleResistance\": " + ble_resistance + "}";
                byte[] data = Encoding.UTF8.GetBytes(jsonString);
                udpClient.Send(data, data.Length, serverIP, serverPort);

                Debug.Log("Data sent: " + jsonString);
            }
            catch (Exception e)
            {
                Debug.LogError("Error sending data via UDP: " + e.Message);
            }

            lastBleFanValue = currentBleFanValue;
            lastBleInclineValue = currentBleInclineValue;
        }
    }
}
