package com.example.qr;

import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.zxing.Result;
import com.karumi.dexter.Dexter;
import com.karumi.dexter.PermissionToken;
import com.karumi.dexter.listener.PermissionDeniedResponse;
import com.karumi.dexter.listener.PermissionGrantedResponse;
import com.karumi.dexter.listener.PermissionRequest;
import com.karumi.dexter.listener.single.PermissionListener;

import org.json.JSONException;
import org.json.JSONObject;

import me.dm7.barcodescanner.zxing.ZXingScannerView;

public class MainActivity extends AppCompatActivity implements ZXingScannerView.ResultHandler {
    private ZXingScannerView scannerView;
    private TextView txtResult;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        scannerView = (ZXingScannerView) findViewById(R.id.a);
        txtResult = (TextView) findViewById(R.id.textView);

        Dexter.withActivity(this)
                .withPermission(Manifest.permission.CAMERA)
                .withListener(new PermissionListener() {
                    @Override
                    public void onPermissionGranted(PermissionGrantedResponse response) {
                        scannerView.setResultHandler(MainActivity.this);
                        scannerView.startCamera();
                    }

                    @Override
                    public void onPermissionDenied(PermissionDeniedResponse response) {
                        Toast.makeText(MainActivity.this, "you must accept this permission", Toast.LENGTH_LONG).show();


                    }

                    @Override
                    public void onPermissionRationaleShouldBeShown(PermissionRequest permission, PermissionToken token) {

                    }
                })
                .check();
    }

    @Override
    protected void onDestroy() {
        scannerView.stopCamera();
        super.onDestroy();
    }

    @Override
    public void handleResult(Result rawResult) {
            txtResult.setText(rawResult.getText());
        scannerView.startCamera();

        // Instantiate the RequestQueue.
        RequestQueue queue = Volley.newRequestQueue(this);
        String url ="http://10.42.0.1:8000/api/search/" + rawResult.getText();

        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string.
                        txtResult.setText("Response is: "+ response);
                        try {
                            JSONObject jsonObject = new JSONObject(response);
                            String laptop_name = jsonObject.getString("laptop_name");
                            String laptop_model = jsonObject.getString("laptop_model");
                            String serial_number = jsonObject.getString("serial_number");

                            JSONObject ownerJsonObject = jsonObject.getJSONObject("owner");
                            String owner_first_name = ownerJsonObject.getString("owner_first_name");
                            String owner_id = ownerJsonObject.getString("owner_id");
                            String image = ownerJsonObject.getString("image");
                            String occ = ownerJsonObject.getString("occ");
                            String dept = ownerJsonObject.getString("dept");

                            Intent intent = new Intent(MainActivity.this, ResultActivity.class);
                            intent.putExtra("image_url", image);
                            intent.putExtra("laptop_name",laptop_name);
                            intent.putExtra("laptop_model",laptop_model);
                            intent.putExtra("serial_number",serial_number);
                            intent.putExtra("owner_first_name", owner_first_name);
                            intent.putExtra("occ",occ);
                            intent.putExtra("owner_id",owner_id);
                            intent.putExtra("dept",dept);

                            startActivity(intent);

                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                txtResult.setText("That didn't work!");
            }
        });

// Add the request to the RequestQueue.
        queue.add(stringRequest);
    }
}