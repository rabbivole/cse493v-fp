using System.Collections;
using System.Collections.Generic;
using System.Net;
using System;
using System.Net.Sockets;
using System.Threading;
using System.Text;
using UnityEngine;

// overall structure pilfered from here but i didn't bother extracting any of their unity files
// https://www.kodeco.com/5475-introduction-to-using-opencv-with-unity#toc-anchor-005
// this is nice because i didn't have to pay 100 dollars for the opencv plugin

public class UpdatePosition : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    int port = 7999;
    string lastData = null;
    string lastConsumedData = null;
    

    // Start is called before the first frame update
    void Start()
    {
        InitUDP();
    }

    // Update is called once per frame
    void Update()
    {
        if (lastConsumedData != null && lastConsumedData != lastData)
        {
            Debug.Log("got data: " + lastData);
            lastConsumedData = lastData;
            // do our positional update
            Vector3 newPos = ConvertToVector(lastData);
            transform.position = newPos;
        } 
        else if (lastConsumedData == null) // first time it runs
        {
            Debug.Log("got data: " + lastData);
            lastConsumedData = lastData;
        }
        // presumably poll for positional data here somehow
        // Vector3 newPos = new Vector3(x, y, z);
        // transform.Translate(newPos - oldPos);
    }

    private Vector3 ConvertToVector(string dataString)
    {
        string[] split = dataString.Split(" ");
        // x in unity space is -camx
        float xUnity = float.Parse(split[0].Substring(2)) * -1;
        // y in unity space is -camz
        float yUnity = float.Parse(split[2].Substring(2)) * -1;
        // z in unity space is +camy
        float zUnity = float.Parse(split[1].Substring(2));
        return new Vector3(xUnity, yUnity, zUnity);

    }

    private void InitUDP()
    {
        Debug.Log("UDP connection get!");
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true; // run alongside other code, supposedly
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (true)
        {
            try
            {
                // unclear why this is 0.0.0.0 and not localhost
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port);

                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                if (text.StartsWith("X")) { // this needs to mark whatever our data starts with
                    lastData = text;
                }
            } 
            catch (Exception e)
            {
                Debug.Log("err: " + e.ToString());
            }
        }
    }
}
